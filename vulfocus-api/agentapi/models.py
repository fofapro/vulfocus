from django.db import models


class AgentRun(models.Model):
    """One disposable agent identity and one challenge, independent of UI users."""
    run_key = models.CharField(max_length=128, unique=True)
    challenge_key = models.CharField(max_length=160)
    token_sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=24, default='created')
    generation = models.PositiveIntegerField(default=0)
    project = models.CharField(max_length=63, default='')
    flag_sha256 = models.CharField(max_length=64, default='')
    solved = models.BooleanField(default=False)
    entrypoints = models.TextField(default='{}')
    error = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_run'
