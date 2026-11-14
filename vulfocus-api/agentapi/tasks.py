import hashlib
import uuid

from celery import shared_task
from .models import AgentRun
from . import runtime


@shared_task(name='agentapi.launch')
def launch(run_id, restart=False):
    run = AgentRun.objects.get(pk=run_id)
    if run.status not in ('starting', 'restarting'):
        return
    try:
        if restart:
            runtime.stop_run(run)
            run.generation += 1
        else:
            if run.project:
                runtime.stop_run(run)
            run.generation = 1
        # Keep the flag shape used by the original Vulfocus launch paths so
        # existing challenge images that recognize it behave the same way.
        flag = 'flag-{bmh%s}' % uuid.uuid4()
        run.flag_sha256 = hashlib.sha256(flag.encode()).hexdigest()
        run.project = 'vfa-%s-%s' % (run.pk, run.generation)
        run.entrypoints = '{}'
        run.error = ''
        accepted = AgentRun.objects.filter(pk=run_id,
            status__in=('starting', 'restarting')).update(
                generation=run.generation, flag_sha256=run.flag_sha256,
                project=run.project, entrypoints='{}', error='')
        if not accepted:
            return
        # Archive verification and import may be slow. Keep it outside the
        # per-run lock so cancellation can be requested while it proceeds.
        runtime.ensure_images(runtime.unit(run.challenge_key))
        run_lock = runtime.locked('run-%s' % run_id)
        try:
            project, endpoints = runtime.start_run(run, flag, images_ready=True)
            import json
            updated = AgentRun.objects.filter(pk=run_id,
                status__in=('starting', 'restarting')).update(
                    project=project, entrypoints=json.dumps(endpoints), status='running')
            if not updated:
                # Cleanup may have been requested during Compose startup.
                # Stop before letting halt report the run as stopped.
                runtime.stop_run(run)
                return
        finally:
            run_lock.close()
    except Exception as exc:
        try:
            runtime.capture_failure(run)
        except Exception:
            pass  # Diagnostic collection must never prevent target cleanup.
        try:
            runtime.stop_run(run)
            runtime.release_images(run)
        except Exception as cleanup_error:
            run.error = '%s；清理失败：%s' % (exc, cleanup_error)
        else:
            run.error = str(exc)
        AgentRun.objects.filter(pk=run_id,
            status__in=('starting', 'restarting')).update(
                status='failed', error=run.error)


@shared_task(name='agentapi.halt')
def halt(run_id):
    run_lock = runtime.locked('run-%s' % run_id)
    run = None
    try:
        # Re-read after taking the lock: launch may have advanced the
        # generation or completed startup while this task waited.
        run = AgentRun.objects.get(pk=run_id)
        try:
            runtime.stop_run(run)
            run.status = 'stopped'
            run.error = ''
            run.entrypoints = '{}'
            run.save()
        except Exception as exc:
            run.status = 'failed'
            run.error = '停止失败：' + str(exc)
            run.save()
    finally:
        run_lock.close()
    if run is not None and run.status == 'stopped':
        try:
            runtime.release_images(run)
        except Exception:
            pass  # The target is stopped; image reclamation can be retried.
