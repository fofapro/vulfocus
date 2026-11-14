import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import TestCase
from docker.errors import ImageNotFound
from .models import AgentRun


class AgentApiTests(TestCase):
    def setUp(self):
        self.old_secret = os.environ.get('VULFOCUS_AGENT_CONTROL_TOKEN')
        os.environ['VULFOCUS_AGENT_CONTROL_TOKEN'] = 'controller-secret'
        self.token = 't' * 48
        self.control = {'HTTP_X_AGENT_CONTROL_TOKEN': 'controller-secret'}
        self.agent = {'HTTP_X_AGENT_RUN': 'case-1',
                      'HTTP_AUTHORIZATION': 'Bearer ' + self.token}

    def tearDown(self):
        if self.old_secret is None:
            os.environ.pop('VULFOCUS_AGENT_CONTROL_TOKEN', None)
        else:
            os.environ['VULFOCUS_AGENT_CONTROL_TOKEN'] = self.old_secret

    def post(self, path, value=None, **headers):
        return self.client.post('/agent/v1/' + path + '/',
            data=json.dumps(value or {}), content_type='application/json', **headers)

    def provision(self):
        with patch('agentapi.views.runtime.unit', return_value={'status': 'ready'}):
            return self.post('runs', {'run_key': 'case-1',
                'challenge_key': 'catalog/example', 'agent_token': self.token}, **self.control)

    def test_bound_identity_and_no_answer_fields(self):
        self.assertEqual(self.post('runs', {}, **{}).status_code, 401)
        self.assertEqual(self.provision().status_code, 200)
        self.assertEqual(self.provision().status_code, 200)
        self.assertEqual(AgentRun.objects.count(), 1)
        with patch('agentapi.views.runtime.public_challenge', return_value={
                'title': 'Example', 'description': 'question'}):
            response = self.client.get('/agent/v1/challenge/', **self.agent)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('flag', response.content.decode())
        self.assertNotIn('token', response.content.decode())

    def test_submit_and_solved_restart(self):
        self.provision()
        run = AgentRun.objects.get(run_key='case-1')
        run.status = 'running'
        run.generation = 1
        run.flag_sha256 = hashlib.sha256(b'flag-{test}').hexdigest()
        run.save()
        self.assertFalse(self.post('submit', {'flag': 'wrong'}, **self.agent).json()['data']['correct'])
        self.assertTrue(self.post('submit', {'flag': 'flag-{test}'}, **self.agent).json()['data']['correct'])
        self.assertEqual(self.post('restart', {}, **self.agent).status_code, 409)
        result = self.client.get('/agent/v1/result/?run_key=case-1', **self.control).json()['data']
        self.assertTrue(result['solved'])

    @patch('agentapi.views.launch.delay')
    def test_start_is_idempotent(self, delay):
        self.provision()
        self.assertEqual(self.post('start', {}, **self.agent).status_code, 202)
        self.assertEqual(self.post('start', {}, **self.agent).status_code, 202)
        self.assertEqual(delay.call_count, 1)

    @patch('agentapi.tasks.runtime.stop_run')
    @patch('agentapi.tasks.runtime.start_run')
    def test_cancellation_during_start_cannot_resurrect_run(self, start_run, stop_run):
        from .tasks import launch
        self.provision()
        run = AgentRun.objects.get(run_key='case-1')
        run.status = 'starting'
        run.save()

        def cancelled(current, flag, images_ready=False):
            self.assertTrue(images_ready)
            AgentRun.objects.filter(pk=current.pk).update(status='stopping')
            return current.project, {'80/tcp': '127.0.0.1:30000'}

        start_run.side_effect = cancelled
        with patch('agentapi.tasks.runtime.unit', return_value={'tasks': []}), \
             patch('agentapi.tasks.runtime.ensure_images'), \
             patch('agentapi.tasks.runtime.locked', return_value=io.StringIO()):
            launch.run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.status, 'stopping')
        stop_run.assert_called_once()

    @patch('agentapi.tasks.runtime.release_images')
    @patch('agentapi.tasks.runtime.stop_run')
    def test_halt_reads_latest_generation_after_run_lock(self, stop_run, release):
        from .tasks import halt
        self.provision()
        run = AgentRun.objects.get(run_key='case-1')
        run.status = 'stopping'
        run.generation = 1
        run.project = 'old-project'
        run.save()

        def acquire(name):
            self.assertEqual(name, 'run-%s' % run.pk)
            AgentRun.objects.filter(pk=run.pk).update(
                generation=2, project='new-project')
            return io.StringIO()

        with patch('agentapi.tasks.runtime.locked', side_effect=acquire):
            halt.run(run.pk)
        stopped = stop_run.call_args[0][0]
        self.assertEqual((stopped.generation, stopped.project), (2, 'new-project'))
        run.refresh_from_db()
        self.assertEqual(run.status, 'stopped')
        release.assert_called_once()

    def test_stop_run_removes_project_volumes(self):
        from .runtime import stop_run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'run-7'
            folder.mkdir()
            override = folder / 'generation-2.yml'
            override.write_text('services: {}\n')
            compose = root / 'challenge.yml'
            compose.write_text('services: {}\n')
            run = SimpleNamespace(pk=7, generation=2, project='vfa-7-2',
                                  challenge_key='catalog/example')
            with patch('agentapi.runtime.unit', return_value={}), \
                 patch('agentapi.runtime.compose_path', return_value=compose), \
                 patch('agentapi.runtime.state_root', return_value=root), \
                 patch('agentapi.runtime.command') as command:
                stop_run(run)
            command.assert_called_once_with('vfa-7-2', compose, override,
                ['down', '--remove-orphans', '--volumes'])

    def test_override_replaces_fixed_host_ports(self):
        from .runtime import write_override
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.yml'
            output = Path(directory) / 'override.yml'
            app = Path(directory) / 'app.py'
            app.write_text('app = object()\n')
            source.write_text('services:\n  master:\n    ports:\n      - "8080:8080"\n'
                              '  slave:\n    ports:\n      - "8081:8081"\n')
            with patch.dict(os.environ, {'VULFOCUS_AGENT_OFFLINE_ROOT': directory}):
                write_override(source, 'master', {
                    'vul_flag': 'test-flag',
                    'LANGFLOW_DATABASE_URL': 'sqlite:////app/data/langflow.db'},
                    output, {'master': ['/app/data:uid=1000,gid=0,mode=1777']},
                    {'master': ['/bin/sh', '-c', 'exec app']},
                    {'master': ['NET_ADMIN']},
                    {'master': ['/dev/net/tun:/dev/net/tun']},
                    {'master': [{'source': 'app.py', 'target': '/app/app.py'}]},
                    {'master': ['/bin/sh', '/usr/local/bin/preflight.sh']})
            text = output.read_text()
        self.assertEqual(text.count('!override'), 2)
        self.assertNotIn('8080:8080', text)
        self.assertNotIn('8081:8081', text)
        self.assertIn('vul_flag', text)
        self.assertIn('LANGFLOW_DATABASE_URL', text)
        self.assertIn('/app/data:uid=1000,gid=0,mode=1777', text)
        self.assertIn('exec app', text)
        self.assertIn('NET_ADMIN', text)
        self.assertIn('/dev/net/tun', text)
        self.assertIn(str(app) + ':/app/app.py:ro', text)
        self.assertIn('/usr/local/bin/preflight.sh', text)

    def test_agent_network_uses_configured_per_run_subnet(self):
        from .runtime import challenge_network_subnet, write_override
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'VULFOCUS_AGENT_NETWORK_POOL': '198.18.0.0/15'}):
            source = Path(directory) / 'source.yml'
            output = Path(directory) / 'override.yml'
            source.write_text('services:\n  target:\n    image: example\n')
            first = challenge_network_subnet(1)
            second = challenge_network_subnet(2)
            self.assertEqual(first, '198.18.0.0/27')
            self.assertEqual(second, '198.18.0.32/27')
            write_override(source, 'target', {'vul_flag': 'test'}, output,
                           network_subnet=second)
            text = output.read_text()
            self.assertIn('198.18.0.32/27', text)
            self.assertIn('default:', text)

    def test_read_only_mount_cannot_escape_package(self):
        from .runtime import write_override
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.yml'
            output = Path(directory) / 'override.yml'
            source.write_text('services:\n  target: {}\n')
            with patch.dict(os.environ, {'VULFOCUS_AGENT_OFFLINE_ROOT': directory}):
                with self.assertRaisesRegex(RuntimeError, '只读挂载配置无效'):
                    write_override(source, 'target', {'vul_flag': 'test'}, output,
                                   service_mounts={'target': [
                                       {'source': '../app.py', 'target': '/app/app.py'}]})

    def test_challenge_title_and_flag_status_resolve_by_image_name(self):
        from .runtime import public_challenge
        key = 'catalog/example'
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'compose.yml').write_text(
                'services:\n  target:\n    ports:\n      - "80/tcp"\n')
            Path(directory, 'catalog-api.json').write_text(json.dumps({'imgs': [{
                'image_id': 'different-id', 'image_name': 'vulfocus/example:latest',
                'image_vul_name': 'Example Vulnerability',
                'image_desc': 'Question text', 'is_flag': 1}]}))
            with patch('agentapi.runtime.package_root', return_value=Path(directory)), \
                 patch('agentapi.runtime.unit', return_value={
                     'title': key, 'tasks': ['image-key'],
                     'compose': 'compose.yml', 'services': {'target': 'image-key'}}), \
                 patch('agentapi.runtime.catalog', return_value={
                     'images': {'image-key': {
                         'image': 'vulfocus/example:latest', 'archive_tags': []}}}):
                result = public_challenge(key)
        self.assertEqual(result['title'], 'Example Vulnerability')
        self.assertEqual(result['description'], 'Question text')
        self.assertEqual(result['flag_support_status'], 'supported')

    def test_challenge_description_omits_explicit_payload(self):
        from .runtime import public_challenge, question_description
        self.assertEqual(question_description('An issue. cmd=whoami'), 'An issue.')
        self.assertEqual(question_description('An issue. GET /admin'), 'An issue.')
        self.assertEqual(question_description('An issue. https://example.org/poc'),
                         'An issue.')
        key = 'catalog/example'
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'compose.yml').write_text(
                'services:\n  target:\n    image: example:fixed\n    ports: ["80/tcp"]\n')
            Path(directory, 'catalog-api.json').write_text(json.dumps({'imgs': [{
                'image_id': 'catalog-id', 'image_name': 'example:fixed',
                'image_vul_name': 'Example',
                'image_desc': 'A vulnerable service. Payload: secret test input',
                'is_flag': 1}]}))
            with patch('agentapi.runtime.package_root', return_value=Path(directory)), \
                 patch('agentapi.runtime.unit', return_value={
                     'title': key, 'tasks': ['image-key'],
                     'compose': 'compose.yml', 'services': {'target': 'image-key'}}), \
                 patch('agentapi.runtime.catalog', return_value={
                     'images': {'image-key': {
                         'image': 'example:fixed', 'archive_tags': []}}}):
                result = public_challenge(key)
        self.assertEqual(result['description'], 'A vulnerable service.')

    @patch('agentapi.runtime.locked', side_effect=AssertionError('unnecessary import lock'))
    @patch('agentapi.runtime.client')
    @patch('agentapi.runtime.catalog')
    def test_existing_verified_image_skips_import_lock(self, catalog, docker_client, _lock):
        from .runtime import ensure_images
        catalog.return_value = {'images': {'image-key': {
            'status': 'verified', 'architecture': 'amd64',
            'image_id': 'sha256:expected'}}}
        docker_client.images.get.return_value.id = 'sha256:expected'
        docker_client.images.get.return_value.attrs = {'Os': 'linux',
                                                         'Architecture': 'amd64'}
        ensure_images({'tasks': ['image-key']})
        docker_client.images.get.assert_called_once_with('ctf-offline/runtime:image-key')

    @patch('agentapi.runtime.client')
    @patch('agentapi.runtime.catalog')
    def test_existing_wrong_architecture_is_rejected(self, catalog, docker_client):
        from .runtime import ensure_images
        catalog.return_value = {'images': {'image-key': {
            'status': 'verified', 'architecture': 'amd64',
            'image_id': 'sha256:expected'}}}
        docker_client.images.get.return_value.id = 'sha256:expected'
        docker_client.images.get.return_value.attrs = {'Os': 'linux',
                                                         'Architecture': 'arm64'}
        with self.assertRaisesRegex(RuntimeError, 'linux/amd64'):
            ensure_images({'tasks': ['image-key']})

    def test_provenance_image_is_not_imported_for_prepared_service(self):
        from .runtime import required_images
        self.assertEqual(required_images({'tasks': ['original', 'prepared'],
                         'services': {'target': 'prepared'}}), ['prepared'])

    @patch('agentapi.runtime.client')
    @patch('agentapi.runtime.catalog')
    def test_existing_archive_alias_gets_local_runtime_tag(self, catalog, docker_client):
        from .runtime import ensure_images
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'image.tar.gz').write_bytes(b'verified archive')
            catalog.return_value = {'images': {'image-key': {
                'status': 'verified', 'architecture': 'amd64',
                'image_id': 'sha256:expected', 'archive': 'image.tar.gz',
                'sha256': hashlib.sha256(b'verified archive').hexdigest(),
                'archive_tags': ['mysql:5.7'], 'image_size': 0}}}
            image = Mock()
            image.id = 'sha256:expected'
            image.attrs = {'Os': 'linux', 'Architecture': 'amd64'}
            tagged = [False]

            def get(name):
                if name == 'mysql:5.7' or tagged[0]:
                    return image
                raise ImageNotFound('missing')

            def tag(*_args, **_kwargs):
                tagged[0] = True

            docker_client.images.get.side_effect = get
            image.tag.side_effect = tag
            with patch('agentapi.runtime.package_root', return_value=root), \
                 patch('agentapi.runtime.state_root', return_value=root), \
                 patch('agentapi.runtime.locked', return_value=io.StringIO()), \
                 patch('agentapi.runtime.shutil.disk_usage',
                       return_value=Mock(free=1024 ** 4)):
                ensure_images({'tasks': ['image-key'],
                               'services': {'db': 'image-key'}})
            image.tag.assert_called_once_with('ctf-offline/runtime', tag='image-key')
            managed = json.loads((root / 'managed-images.json').read_text())
            self.assertEqual(managed['image-key'], ['ctf-offline/runtime:image-key'])

    @patch('agentapi.runtime.compose_path', side_effect=AssertionError('started after cancellation'))
    @patch('agentapi.runtime.ensure_images')
    @patch('agentapi.runtime.unit', return_value={'tasks': ['image-key']})
    def test_cancelled_during_import_does_not_start(self, _unit, _images, _compose):
        from .runtime import start_run
        self.provision()
        run = AgentRun.objects.get(run_key='case-1')
        run.status = 'stopped'
        run.save()
        with self.assertRaisesRegex(RuntimeError, '已取消'):
            start_run(run, 'flag-{test}')

    @patch('agentapi.runtime.containers')
    def test_early_exit_reports_service_and_exit_code(self, containers):
        from .runtime import wait_ready
        container = Mock()
        container.status = 'exited'
        container.attrs = {'Config': {'Labels': {
            'com.docker.compose.service': 'target'}},
            'State': {'ExitCode': 127, 'OOMKilled': False}}
        containers.return_value = [container]
        with self.assertRaisesRegex(RuntimeError, 'target exit=127 oom=False'):
            wait_ready('project', 'target')

    @patch('agentapi.runtime.containers')
    def test_failure_diagnostic_is_private_and_redacts_flag(self, containers):
        from .runtime import capture_failure
        container = Mock()
        container.attrs = {'Config': {'Labels': {
            'com.docker.compose.service': 'target'}},
            'State': {'ExitCode': 1, 'OOMKilled': False}}
        container.logs.return_value = b'error flag-{hidden-value}'
        containers.return_value = [container]
        with tempfile.TemporaryDirectory() as directory, \
             patch('agentapi.runtime.state_root', return_value=Path(directory)):
            capture_failure(SimpleNamespace(pk=12, generation=1, project='test'))
            path = Path(directory) / 'run-12/startup-failure-1.json'
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            text = path.read_text()
            self.assertIn('[redacted-flag]', text)
            self.assertNotIn('hidden-value', text)
