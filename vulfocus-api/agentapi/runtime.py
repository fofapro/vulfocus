"""Offline-only Docker lifecycle for agent runs.

The solver never receives a Docker socket or an archive path. The API and
Celery worker need the same read-only package mount and writable state mount.
"""
import fcntl
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
from docker.errors import ImageNotFound

from django.conf import settings
from vulfocus.settings import client, api_docker_client, VUL_IP


def package_root():
    root = os.environ.get('VULFOCUS_AGENT_OFFLINE_ROOT', '')
    if not root:
        raise RuntimeError('VULFOCUS_AGENT_OFFLINE_ROOT 未配置')
    return Path(root).resolve()


def state_root():
    root = Path(os.environ.get('VULFOCUS_AGENT_STATE_DIR',
                               str(package_root() / 'data/agent-runs')))
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def catalog():
    with (package_root() / 'manifest.json').open() as stream:
        return json.load(stream)


def unit(key):
    if not key.startswith('catalog/'):
        raise ValueError('仅允许目录中的独立题目')
    item = catalog()['units'].get(key)
    if not item or item.get('status') != 'ready' or not item.get('compose'):
        raise ValueError('题目资源未齐全或不是独立题目')
    return item


def public_challenge(key):
    item = unit(key)
    manifest = catalog()
    record = None
    fallback_name = ''
    source = package_root() / 'catalog-api.json'
    if source.is_file():
        import yaml
        suffix = key.rsplit('/', 1)[-1]
        images = json.loads(source.read_text()).get('imgs', [])
        by_id = {image.get('image_id'): image for image in images}
        by_name = {image.get('image_name'): image for image in images}
        record = by_id.get(suffix)
        if not record:
            compose_services = yaml.safe_load(compose_path(item).read_text())['services']
            exposed = [name for name, service in compose_services.items()
                       if service.get('ports') and name not in
                       ('db', 'mysql', 'redis', 'mongo', 'mongodb', 'postgres')]
            for service_name in exposed:
                image_key = item.get('services', {}).get(service_name)
                if not image_key:
                    continue
                image = manifest['images'][image_key]
                for name in [image.get('image')] + image.get('archive_tags', []):
                    if not name:
                        continue
                    if name.startswith('docker.io/'):
                        name = name[len('docker.io/'):]
                    if not fallback_name and not name.startswith('ctf-offline/'):
                        fallback_name = name.rsplit(':', 1)[0]
                    record = by_name.get(name)
                    if record:
                        break
                if record:
                    break
    title = item.get('title') or key
    if title == key:
        title = ((record or {}).get('image_vul_name') or fallback_name or key)
    flag_status = ('generated' if not record else
                   'supported' if str(record.get('is_flag')) == '1' else 'unsupported')
    description = question_description((record or {}).get('image_desc') or '')
    return {'challenge_key': key, 'title': title,
            'description': description,
            'flag_supported': flag_status != 'unsupported',
            'flag_support_status': flag_status}


def question_description(source):
    """Keep context while dropping catalog text that starts an exploit recipe."""
    marker = re.search(
        r'payload|\bpoc\b|\bexp\b|利用方法|利用方式|复现步骤|复现方法|测试步骤|'
        r'攻击步骤|curl\s|wget\s|https?://|<code|<pre|```|'
        r'\b(?:GET|POST|PUT|DELETE)\s+/|cmd\s*=|/etc/passwd|\bwhoami\b|\bid;',
        source, re.IGNORECASE)
    if marker:
        source = source[:marker.start()]
    return source.split('\n\n', 1)[0].strip()[:600]


def compose_path(item):
    root = package_root()
    path = (root / item['compose']).resolve()
    if root not in path.parents or not path.is_file():
        raise RuntimeError('离线编排文件无效')
    return path


def locked(name):
    """Caller closes the returned file after releasing flock."""
    path = state_root() / (name + '.lock')
    stream = path.open('a+')
    fcntl.flock(stream, fcntl.LOCK_EX)
    return stream


def verify_loaded_image(image, record, image_key):
    if image.id != record['image_id']:
        raise RuntimeError('本地镜像与离线清单的固定版本不一致：' + image_key)
    if image.attrs.get('Os') != 'linux' or image.attrs.get('Architecture') != 'amd64':
        raise RuntimeError('本地镜像不是 linux/amd64：' + image_key)


def required_images(item):
    """Only service images are needed to launch; other tasks are provenance."""
    archived = set(item.get('tasks') or [])
    used = list(dict.fromkeys((item.get('services') or {}).values()))
    if not used:
        used = list(item.get('tasks') or [])
    if not set(used).issubset(archived):
        raise RuntimeError('编排引用了清单之外的镜像')
    return used


def ensure_images(item):
    manifest = catalog()
    image_keys = required_images(item)
    # Reusing an already verified local image must not wait behind an unrelated
    # multi-gigabyte import; in particular, an active solver may restart its
    # own challenge while a catalog audit imports other images.
    all_present = True
    for image_key in image_keys:
        record = manifest['images'].get(image_key)
        if not record or record.get('status') != 'verified':
            raise RuntimeError('镜像归档未通过校验：' + image_key)
        if record.get('architecture') != 'amd64':
            raise RuntimeError('镜像架构不是 amd64：' + image_key)
        try:
            present = client.images.get('ctf-offline/runtime:' + image_key)
            verify_loaded_image(present, record, image_key)
        except ImageNotFound:
            all_present = False
    if all_present:
        return
    managed_path = state_root() / 'managed-images.json'
    for image_key in image_keys:
        image_lock = locked('image-import-key-' + hashlib.sha256(
            image_key.encode('utf-8')).hexdigest()[:24])
        try:
            record = manifest['images'].get(image_key)
            if not record or record.get('status') != 'verified':
                raise RuntimeError('镜像归档未通过校验：' + image_key)
            if record.get('architecture') != 'amd64':
                raise RuntimeError('镜像架构不是 amd64：' + image_key)
            tag = 'ctf-offline/runtime:' + image_key
            try:
                present = client.images.get(tag)
                verify_loaded_image(present, record, image_key)
                continue
            except ImageNotFound:
                pass
            # Separate images can load concurrently. Limit Docker imports to
            # twenty lanes; the per-image lock prevents duplicate imports.
            slot = None
            while slot is None:
                for number in range(20):
                    candidate = (state_root() /
                                 ('image-import-slot-%s.lock' % number)).open('a+')
                    try:
                        fcntl.flock(candidate, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        slot = candidate
                        break
                    except BlockingIOError:
                        candidate.close()
                if slot is None:
                    time.sleep(0.5)
            try:
                # Recheck after waiting for a slot: another worker may have
                # loaded this image while we were waiting.
                try:
                    present = client.images.get(tag)
                    verify_loaded_image(present, record, image_key)
                    continue
                except ImageNotFound:
                    pass
                root = package_root()
                archive = (root / record['archive']).resolve()
                if root not in archive.parents or not archive.is_file():
                    raise RuntimeError('镜像归档缺失：' + image_key)
                digest = hashlib.sha256()
                with archive.open('rb') as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b''):
                        digest.update(chunk)
                if digest.hexdigest() != record['sha256']:
                    raise RuntimeError('镜像归档校验失败：' + image_key)
                free = shutil.disk_usage(str(state_root())).free
                minimum = int(os.environ.get('VULFOCUS_AGENT_MIN_FREE_GIB', '10')) * 1024 ** 3
                if free - int(record.get('image_size', 0)) < minimum:
                    raise RuntimeError('导入后资源卷可用空间会低于预留阈值')
                archive_tags = record.get('archive_tags') or []
                if not archive_tags:
                    raise RuntimeError('镜像归档没有可导入标签：' + image_key)
                new_tags = []
                existing_alias = None
                for archive_tag in archive_tags:
                    try:
                        candidate = client.images.get(archive_tag)
                        verify_loaded_image(candidate, record, image_key)
                        existing_alias = candidate
                    except ImageNotFound:
                        new_tags.append(archive_tag)
                if existing_alias:
                    existing_alias.tag('ctf-offline/runtime', tag=image_key)
                    new_tags = [tag]
                else:
                    # Docker accepts the compressed archive directly.
                    import docker
                    timeout = int(os.environ.get('VULFOCUS_AGENT_IMAGE_LOAD_TIMEOUT', '1800'))
                    if timeout < 60:
                        raise RuntimeError('镜像导入超时必须至少为 60 秒')
                    loader = docker.APIClient(base_url='unix:///var/run/docker.sock',
                                              version=api_docker_client._version,
                                              timeout=timeout)
                    try:
                        with archive.open('rb') as source:
                            for event in loader.load_image(source, quiet=True):
                                if event.get('error'):
                                    raise RuntimeError('Docker 导入失败：' + event['error'])
                    finally:
                        loader.close()
                    if tag not in archive_tags:
                        loaded = client.images.get(archive_tags[0])
                        verify_loaded_image(loaded, record, image_key)
                        loaded.tag('ctf-offline/runtime', tag=image_key)
                        new_tags.append(tag)
                imported = client.images.get(tag)
                verify_loaded_image(imported, record, image_key)
                # Serialize only the small bookkeeping update and image
                # reclamation, never the multi-gigabyte Docker load.
                lock = locked('image-import')
                try:
                    managed = (json.loads(managed_path.read_text())
                               if managed_path.exists() else {})
                    managed[image_key] = new_tags
                    temporary = managed_path.with_suffix('.tmp')
                    temporary.write_text(json.dumps(managed))
                    os.replace(str(temporary), str(managed_path))
                finally:
                    lock.close()
            finally:
                slot.close()
        finally:
            image_lock.close()


def primary_service(compose):
    import yaml
    data = yaml.safe_load(compose.read_text())
    services = data.get('services') or {}
    if not services:
        raise RuntimeError('编排文件没有服务')
    return 'target' if 'target' in services else next(iter(services))


def challenge_network_subnet(run_id):
    """Use a small, repeatable subnet instead of exhausting Docker's defaults."""
    value = os.environ.get('VULFOCUS_AGENT_NETWORK_POOL')
    if not value:
        return None
    pool = ipaddress.ip_network(value, strict=True)
    prefix = 27  # 30 usable addresses cover every supported Compose scenario.
    if pool.version != 4 or pool.prefixlen > prefix:
        raise RuntimeError('题目网络池必须是至少一个 /27 的 IPv4 网段')
    slots = 1 << (prefix - pool.prefixlen)
    index = (int(run_id) - 1) % slots
    return str(ipaddress.ip_network((int(pool.network_address) + index * 32,
                                     prefix)))


def write_override(compose, target, environment, destination,
                   service_tmpfs=None, service_commands=None,
                   service_cap_add=None, service_devices=None,
                   service_mounts=None, service_entrypoints=None,
                   network_subnet=None):
    """Publish each container port on a fresh host port for this run.

    The offline catalog preserves upstream Compose files, some of which pin
    host ports. Compose's !override tag replaces those bindings rather than
    merging another list on top of them.
    """
    import yaml
    class OverrideList(list):
        pass
    class Dumper(yaml.SafeDumper):
        pass
    Dumper.add_representer(OverrideList,
        lambda dumper, value: dumper.represent_sequence('!override', value))
    source = yaml.safe_load(compose.read_text())
    services = {}
    service_tmpfs = service_tmpfs or {}
    service_commands = service_commands or {}
    service_cap_add = service_cap_add or {}
    service_devices = service_devices or {}
    service_mounts = service_mounts or {}
    service_entrypoints = service_entrypoints or {}
    unknown = (set(service_tmpfs) | set(service_commands) |
               set(service_cap_add) | set(service_devices) |
               set(service_mounts) | set(service_entrypoints)) - set(source.get('services') or {})
    if unknown:
        raise RuntimeError('临时目录配置指向未知服务：' + ', '.join(sorted(unknown)))
    for name, original in (source.get('services') or {}).items():
        patch = {'environment': ({**environment} if name == target else
                                 {'vul_flag': environment['vul_flag']})}
        if original.get('ports'):
            patch['ports'] = OverrideList([
                str(port).rsplit(':', 1)[-1] for port in original['ports']])
        if name in service_tmpfs:
            values = service_tmpfs[name]
            if not isinstance(values, list) or not all(
                    isinstance(value, str) and value.startswith('/') for value in values):
                raise RuntimeError('临时目录配置无效：' + name)
            patch['tmpfs'] = values
        if name in service_commands:
            command = service_commands[name]
            if not isinstance(command, list) or not command or not all(
                    isinstance(part, str) and part for part in command):
                raise RuntimeError('启动命令配置无效：' + name)
            patch['command'] = command
        if name in service_entrypoints:
            entrypoint = service_entrypoints[name]
            if (not isinstance(entrypoint, list) or not entrypoint or
                    not all(isinstance(part, str) and part for part in entrypoint) or
                    not entrypoint[0].startswith('/')):
                raise RuntimeError('入口命令配置无效：' + name)
            patch['entrypoint'] = entrypoint
        if name in service_cap_add:
            caps = service_cap_add[name]
            if not isinstance(caps, list) or not caps or not all(
                    isinstance(cap, str) and re.fullmatch(r'[A-Z_]+', cap)
                    and cap != 'ALL' for cap in caps):
                raise RuntimeError('容器能力配置无效：' + name)
            patch['cap_add'] = caps
        if name in service_devices:
            devices = service_devices[name]
            if not isinstance(devices, list) or not devices:
                raise RuntimeError('容器设备配置无效：' + name)
            for device in devices:
                parts = device.split(':') if isinstance(device, str) else []
                if (len(parts) not in (2, 3) or not parts[0].startswith('/dev/')
                        or not parts[1].startswith('/dev/') or
                        'docker.sock' in device or
                        (len(parts) == 3 and parts[2] not in ('r', 'w', 'rw', 'rwm'))):
                    raise RuntimeError('容器设备配置无效：' + name)
            patch['devices'] = devices
        if name in service_mounts:
            mounts = service_mounts[name]
            if not isinstance(mounts, list) or not mounts:
                raise RuntimeError('只读挂载配置无效：' + name)
            bindings = []
            root = package_root()
            for mount in mounts:
                if not isinstance(mount, dict) or set(mount) != {'source', 'target'}:
                    raise RuntimeError('只读挂载配置无效：' + name)
                relative = mount['source']
                destination_path = mount['target']
                if (not isinstance(relative, str) or not relative or
                        ':' in relative or '\n' in relative or
                        Path(relative).is_absolute() or '..' in Path(relative).parts or
                        not isinstance(destination_path, str) or
                        not destination_path.startswith('/') or
                        ':' in destination_path or '\n' in destination_path or
                        '..' in Path(destination_path).parts):
                    raise RuntimeError('只读挂载配置无效：' + name)
                host_path = (root / relative).resolve()
                if root not in host_path.parents or not host_path.is_file():
                    raise RuntimeError('只读挂载源文件不存在：' + relative)
                bindings.append('%s:%s:ro' % (host_path, destination_path))
            patch['volumes'] = bindings
        if patch:
            services[name] = patch
    override = {'services': services}
    if network_subnet:
        subnet = ipaddress.ip_network(network_subnet, strict=True)
        if subnet.version != 4 or subnet.prefixlen != 27:
            raise RuntimeError('题目网络必须是 /27 IPv4 网段')
        override['networks'] = {'default': {'ipam': {'config': [
            {'subnet': str(subnet)}]}}}
    destination.write_text(yaml.dump(override, Dumper=Dumper,
                                     sort_keys=False))


def command(project, compose, override, operation):
    binary = os.environ.get('VULFOCUS_AGENT_COMPOSE', '/usr/local/bin/docker-compose')
    argv = [binary, '-p', project, '-f', str(compose), '-f', str(override)] + operation
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, timeout=180, env=dict(os.environ, DOCKER_HOST='unix:///var/run/docker.sock'))
    if proc.returncode:
        raise RuntimeError('Compose 失败：' + (proc.stderr or proc.stdout)[-1200:])
    return proc.stdout


def containers(project):
    return client.containers.list(all=True,
        filters={'label': 'com.docker.compose.project=' + project})


def entrypoints(project, service):
    result = {}
    for container in containers(project):
        container.reload()
        labels = container.attrs.get('Config', {}).get('Labels') or {}
        service_name = labels.get('com.docker.compose.service') or service
        ports = container.attrs.get('NetworkSettings', {}).get('Ports') or {}
        for internal, bindings in ports.items():
            if not bindings:
                continue
            name = internal if service_name == service else service_name + '/' + internal
            result[name] = VUL_IP + ':' + bindings[0]['HostPort']
    return result


def wait_ready(project, service):
    deadline = time.monotonic() + 120
    last = '容器尚未运行'
    stable_since = None
    while time.monotonic() < deadline:
        found = containers(project)
        if found:
            for container in found:
                container.reload()
            exited = [c for c in found if c.status == 'exited']
            if exited:
                details = []
                for container in exited:
                    labels = container.attrs.get('Config', {}).get('Labels') or {}
                    state = container.attrs.get('State') or {}
                    name = labels.get('com.docker.compose.service') or container.name
                    details.append('%s exit=%s oom=%s' % (name,
                        state.get('ExitCode'), bool(state.get('OOMKilled'))))
                raise RuntimeError('题目容器提前退出：' + ', '.join(details))
            if all(c.status == 'running' and
                   c.attrs.get('State', {}).get('Health', {}).get('Status') != 'unhealthy'
                   for c in found):
                endpoints = entrypoints(project, service)
                if endpoints:
                    try:
                        for port_name, address in endpoints.items():
                            if port_name.endswith('/udp'):
                                continue
                            host, port = address.rsplit(':', 1)
                            with socket.create_connection((host, int(port)), timeout=2):
                                pass
                        stable_since = stable_since or time.monotonic()
                        if time.monotonic() - stable_since >= 15:
                            return endpoints
                    except OSError as exc:
                        last = str(exc)
                        stable_since = None
                else:
                    raise RuntimeError('题目没有可访问的映射端口')
            else:
                last = ', '.join('%s=%s/%s' % (
                    (c.attrs.get('Config', {}).get('Labels') or {}).get(
                        'com.docker.compose.service', c.name), c.status,
                    (c.attrs.get('State', {}).get('Health') or {}).get('Status', 'none'))
                    for c in found)
                stable_since = None
        time.sleep(2)
    raise RuntimeError('题目未就绪：' + last[:300])


def start_run(run, flag, images_ready=False):
    item = unit(run.challenge_key)
    if not images_ready:
        ensure_images(item)
    # Import can take minutes. A scheduler timeout may have withdrawn the run
    # while it waited, so do not create a target after cancellation.
    from .models import AgentRun
    if not AgentRun.objects.filter(pk=run.pk,
            status__in=('starting', 'restarting')).exists():
        raise RuntimeError('题目启动已取消')
    compose = compose_path(item)
    service = primary_service(compose)
    root = state_root() / ('run-' + str(run.pk))
    root.mkdir(parents=True, exist_ok=True)
    override = root / ('generation-%s.yml' % run.generation)
    environment = {'vul_flag': flag}
    service_tmpfs = {}
    service_commands = {}
    service_cap_add = {}
    service_devices = {}
    service_mounts = {}
    service_entrypoints = {}
    overrides_path = os.environ.get('VULFOCUS_AGENT_OVERRIDES')
    if overrides_path:
        overrides = json.loads(Path(overrides_path).read_text())
        challenge_override = overrides.get(run.challenge_key, {})
        environment.update(challenge_override.get('environment', {}))
        service_tmpfs = challenge_override.get('tmpfs', {})
        service_commands = challenge_override.get('command', {})
        service_cap_add = challenge_override.get('cap_add', {})
        service_devices = challenge_override.get('devices', {})
        service_mounts = challenge_override.get('mounts', {})
        service_entrypoints = challenge_override.get('entrypoint', {})
    write_override(compose, service, environment, override,
                   service_tmpfs, service_commands,
                   service_cap_add, service_devices, service_mounts,
                   service_entrypoints,
                   challenge_network_subnet(run.pk))
    project = 'vfa-%s-%s' % (run.pk, run.generation)
    command(project, compose, override, ['up', '-d', '--no-build', '--pull', 'never'])
    for container in containers(project):
        container.reload()
        if container.status != 'running':
            state = container.attrs.get('State') or {}
            raise RuntimeError('题目容器提前退出：%s exit=%s oom=%s' % (
                container.name, state.get('ExitCode'), bool(state.get('OOMKilled'))))
        try:
            result = container.exec_run(['sh', '-c', 'touch /tmp/' + flag])
            if result.exit_code != 0:
                raise RuntimeError('Flag 文件写入失败')
        except Exception as exc:
            raise RuntimeError('题目不支持本次 Flag 注入：' + str(exc))
    return project, wait_ready(project, service)


def stop_run(run):
    if not run.project:
        return
    item = unit(run.challenge_key)
    compose = compose_path(item)
    directory = state_root() / ('run-' + str(run.pk))
    override = directory / ('generation-%s.yml' % run.generation)
    if not override.is_file():
        override = directory / ('generation-%s.json' % run.generation)
    if override.is_file():
        # Every Agent run has its own Compose project. Remove its anonymous and
        # project-scoped named volumes with the containers so repeated runs do
        # not fill Docker's data partition. Compose preserves external volumes.
        command(run.project, compose, override, ['down', '--remove-orphans', '--volumes'])


def capture_failure(run):
    """Keep bounded, private startup diagnostics before Compose removes containers."""
    if not run.project:
        return
    entries = []
    for container in containers(run.project):
        try:
            container.reload()
            labels = container.attrs.get('Config', {}).get('Labels') or {}
            state = container.attrs.get('State') or {}
            tail = container.logs(tail=80, timestamps=True).decode('utf-8', 'replace')[-8192:]
            tail = re.sub(r'flag-\{[^}]{1,256}\}', '[redacted-flag]', tail)
            entries.append({'service': labels.get('com.docker.compose.service') or
                            container.name, 'exit_code': state.get('ExitCode'),
                            'oom_killed': bool(state.get('OOMKilled')),
                            'state_error': state.get('Error'), 'log_tail': tail})
        except Exception as exc:
            entries.append({'service': container.name,
                            'diagnostic_error': str(exc)[:300]})
    if entries:
        directory = state_root() / ('run-' + str(run.pk))
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / ('startup-failure-%s.json' % run.generation)
        descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, 'w') as output:
            json.dump(entries, output, ensure_ascii=False)


def release_images(run):
    """Remove only tags introduced by this feature and unused by other runs."""
    from .models import AgentRun
    lock = locked('image-import')
    try:
        path = state_root() / 'managed-images.json'
        if not path.exists():
            return
        managed = json.loads(path.read_text())
        # The offline catalog is large; read it once for this release.
        units = catalog()['units']
        needed = set()
        for other in AgentRun.objects.filter(status__in=('starting', 'running', 'restarting', 'stopping')):
            if other.pk != run.pk:
                item = units.get(other.challenge_key)
                if item and item.get('status') == 'ready' and item.get('compose'):
                    needed.update(required_images(item))
        item = units.get(run.challenge_key)
        if not item or item.get('status') != 'ready' or not item.get('compose'):
            raise ValueError('题目资源未齐全或不是独立题目')
        for image_key in required_images(item):
            if image_key in needed or image_key not in managed:
                continue
            remaining = []
            for tag in managed[image_key]:
                try:
                    client.images.remove(tag, force=False)
                except Exception:
                    remaining.append(tag)
            if remaining:
                managed[image_key] = remaining
            else:
                del managed[image_key]
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(managed))
        os.replace(str(temporary), str(path))
    finally:
        lock.close()


def crashed(run):
    """Report a target that died after its initial readiness check."""
    if not run.project:
        return False
    found = containers(run.project)
    return not found or any(c.status != 'running' for c in found)
