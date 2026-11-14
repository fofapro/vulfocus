"""Small, run-bound API for a solving agent and its trusted controller."""
import hashlib
import hmac
import json
import os
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import OperationalError
from django.utils import timezone
import time

from .models import AgentRun
from . import runtime
from .tasks import launch, halt


def reply(data=None, error=None, code=200):
    return JsonResponse({'ok': error is None, 'data': data, 'error': error}, status=code)


def body(request):
    try:
        value = json.loads(request.body or b'{}')
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, UnicodeDecodeError):
        raise ValueError('请求 JSON 无效')


def control(request):
    secret = os.environ.get('VULFOCUS_AGENT_CONTROL_TOKEN', '')
    supplied = request.META.get('HTTP_X_AGENT_CONTROL_TOKEN', '')
    return bool(secret and supplied and hmac.compare_digest(secret, supplied))


def agent(request):
    key = request.META.get('HTTP_X_AGENT_RUN', '')
    authorization = request.META.get('HTTP_AUTHORIZATION', '')
    if not authorization.startswith('Bearer ') or not key:
        return None
    run = AgentRun.objects.filter(run_key=key).first()
    if not run:
        return None
    digest = hashlib.sha256(authorization[7:].encode()).hexdigest()
    return run if hmac.compare_digest(digest, run.token_sha256) else None


def check_method(request, expected):
    return None if request.method == expected else reply(error='方法不允许', code=405)


@csrf_exempt
def runs(request):
    invalid = check_method(request, 'POST')
    if invalid:
        return invalid
    if not control(request):
        return reply(error='未授权', code=401)
    try:
        data = body(request)
        key, challenge_key, token = data['run_key'], data['challenge_key'], data['agent_token']
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', key) or len(token) < 32:
            raise ValueError('运行标识或令牌无效')
        runtime.unit(challenge_key)
        digest = hashlib.sha256(token.encode()).hexdigest()
        for attempt in range(4):
            try:
                run, created = AgentRun.objects.get_or_create(run_key=key,
                    defaults={'challenge_key': challenge_key, 'token_sha256': digest})
                break
            except OperationalError:
                if attempt == 3:
                    raise
                time.sleep(0.5 * (attempt + 1))
        if not created and (run.challenge_key != challenge_key or
                            not hmac.compare_digest(run.token_sha256, digest)):
            return reply(error='运行标识已绑定其他题目或令牌', code=409)
        return reply({'run_key': key, 'challenge_key': challenge_key, 'status': run.status})
    except (KeyError, ValueError) as exc:
        return reply(error=str(exc), code=400)


@csrf_exempt
def result(request):
    invalid = check_method(request, 'GET')
    if invalid:
        return invalid
    if not control(request):
        return reply(error='未授权', code=401)
    run = AgentRun.objects.filter(run_key=request.GET.get('run_key', '')).first()
    if not run:
        return reply(error='运行不存在', code=404)
    return reply({'run_key': run.run_key, 'challenge_key': run.challenge_key,
                  'status': run.status, 'solved': run.solved,
                  'generation': run.generation, 'error': run.error})


@csrf_exempt
def cleanup(request):
    invalid = check_method(request, 'POST')
    if invalid:
        return invalid
    if not control(request):
        return reply(error='未授权', code=401)
    try:
        key = body(request)['run_key']
    except (KeyError, ValueError) as exc:
        return reply(error=str(exc), code=400)
    run = AgentRun.objects.filter(run_key=key).first()
    if not run:
        return reply(error='运行不存在', code=404)
    if AgentRun.objects.filter(pk=run.pk, status__in=(
            'starting', 'running', 'restarting', 'failed')).update(
                status='stopping', updated_at=timezone.now()):
        halt.delay(run.pk)
        return reply({'status': 'stopping', 'solved': run.solved})
    run.refresh_from_db()
    return reply({'status': run.status, 'solved': run.solved})


def challenge(request):
    invalid = check_method(request, 'GET')
    if invalid:
        return invalid
    run = agent(request)
    if not run:
        return reply(error='未授权', code=401)
    return reply(runtime.public_challenge(run.challenge_key))


@csrf_exempt
def start(request):
    invalid = check_method(request, 'POST')
    if invalid:
        return invalid
    run = agent(request)
    if not run:
        return reply(error='未授权', code=401)
    if run.status == 'running':
        return reply({'status': 'running', 'entrypoints': json.loads(run.entrypoints)})
    if run.status == 'starting':
        return reply({'status': 'starting'}, code=202)
    if run.status not in ('created', 'failed', 'stopped') or run.solved:
        return reply(error='当前状态不能启动', code=409)
    updated = AgentRun.objects.filter(pk=run.pk,
        status__in=('created', 'failed', 'stopped'), solved=False).update(
            status='starting', error='', updated_at=timezone.now())
    if not updated:
        return reply(error='状态已变化，请查询状态后重试', code=409)
    launch.delay(run.pk)
    return reply({'status': 'starting'}, code=202)


def status(request):
    invalid = check_method(request, 'GET')
    if invalid:
        return invalid
    run = agent(request)
    if not run:
        return reply(error='未授权', code=401)
    if run.status == 'running' and runtime.crashed(run):
        run.status = 'failed'
        run.error = '题目容器在就绪后退出'
        run.save(update_fields=['status', 'error', 'updated_at'])
    return reply({'status': run.status, 'generation': run.generation,
                  'entrypoints': json.loads(run.entrypoints), 'solved': run.solved,
                  'error': run.error})


@csrf_exempt
def submit(request):
    invalid = check_method(request, 'POST')
    if invalid:
        return invalid
    run = agent(request)
    if not run:
        return reply(error='未授权', code=401)
    if run.status != 'running':
        return reply(error='题目未运行', code=409)
    try:
        flag = body(request)['flag']
        if not isinstance(flag, str) or not 1 <= len(flag) <= 255:
            raise ValueError('Flag 无效')
    except (KeyError, ValueError) as exc:
        return reply(error=str(exc), code=400)
    correct = hmac.compare_digest(hashlib.sha256(flag.encode()).hexdigest(), run.flag_sha256)
    if correct:
        updated = AgentRun.objects.filter(pk=run.pk, status='running',
            flag_sha256=run.flag_sha256).update(solved=True,
                updated_at=timezone.now())
        if not updated:
            return reply(error='题目状态已变化，请重新查询', code=409)
    return reply({'correct': correct, 'solved': run.solved or correct})


@csrf_exempt
def stop(request):
    invalid = check_method(request, 'POST')
    if invalid:
        return invalid
    run = agent(request)
    if not run:
        return reply(error='未授权', code=401)
    if run.status in ('stopped', 'created'):
        return reply({'status': run.status})
    if run.status == 'stopping':
        return reply({'status': 'stopping'}, code=202)
    if run.status not in ('running', 'failed'):
        return reply(error='当前状态不能停止', code=409)
    updated = AgentRun.objects.filter(pk=run.pk,
        status__in=('running', 'failed')).update(
            status='stopping', updated_at=timezone.now())
    if not updated:
        return reply(error='状态已变化，请查询状态后重试', code=409)
    halt.delay(run.pk)
    return reply({'status': 'stopping'}, code=202)


@csrf_exempt
def restart(request):
    invalid = check_method(request, 'POST')
    if invalid:
        return invalid
    run = agent(request)
    if not run:
        return reply(error='未授权', code=401)
    if run.solved:
        return reply(error='已判通过的运行不能重启', code=409)
    if run.status == 'restarting':
        return reply({'status': 'restarting'}, code=202)
    if run.status not in ('running', 'stopped', 'failed') or not run.generation:
        return reply(error='当前状态不能重启', code=409)
    updated = AgentRun.objects.filter(pk=run.pk,
        status__in=('running', 'stopped', 'failed'), solved=False,
        generation__gt=0).update(status='restarting',
                                 updated_at=timezone.now())
    if not updated:
        return reply(error='状态已变化，请查询状态后重试', code=409)
    launch.delay(run.pk, True)
    return reply({'status': 'restarting'}, code=202)
