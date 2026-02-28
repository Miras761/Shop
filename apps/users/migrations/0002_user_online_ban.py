from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Последний визит'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_banned',
            field=models.BooleanField(default=False, verbose_name='Заблокирован'),
        ),
        migrations.AddField(
            model_name='user',
            name='ban_reason',
            field=models.TextField(blank=True, verbose_name='Причина блокировки'),
        ),
        migrations.AddField(
            model_name='user',
            name='warnings_count',
            field=models.IntegerField(default=0, verbose_name='Предупреждений'),
        ),
    ]
