from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(
        name='AgentRun',
        fields=[
            ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('run_key', models.CharField(max_length=128, unique=True)),
            ('challenge_key', models.CharField(max_length=160)),
            ('token_sha256', models.CharField(max_length=64)),
            ('status', models.CharField(default='created', max_length=24)),
            ('generation', models.PositiveIntegerField(default=0)),
            ('project', models.CharField(default='', max_length=63)),
            ('flag_sha256', models.CharField(default='', max_length=64)),
            ('solved', models.BooleanField(default=False)),
            ('entrypoints', models.TextField(default='{}')),
            ('error', models.TextField(default='')),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
        ],
        options={'db_table': 'agent_run'},
    )]
