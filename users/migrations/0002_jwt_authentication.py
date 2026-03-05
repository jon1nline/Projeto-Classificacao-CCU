# Generated migration for JWT-related models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('login_time', models.DateTimeField(auto_now_add=True)),
                ('logout_time', models.DateTimeField(blank=True, null=True)),
                ('is_successful', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-login_time'],
            },
        ),
        migrations.CreateModel(
            name='RevokedToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_id', models.CharField(max_length=255, unique=True)),
                ('revoked_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(
                    choices=[
                        ('logout', 'Logout voluntário'),
                        ('password_change', 'Senha alterada'),
                        ('account_disabled', 'Conta desativada'),
                        ('suspicious_activity', 'Atividade suspeita'),
                        ('admin_revoke', 'Revogação administrativa'),
                    ],
                    default='logout',
                    max_length=50
                )),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revoked_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-revoked_at'],
            },
        ),
        migrations.AddIndex(
            model_name='userloginhistory',
            index=models.Index(fields=['user', '-login_time'], name='users_userlo_user_id_login__idx'),
        ),
        migrations.AddIndex(
            model_name='revokedtoken',
            index=models.Index(fields=['token_id'], name='users_revoke_token_i_idx'),
        ),
        migrations.AddIndex(
            model_name='revokedtoken',
            index=models.Index(fields=['user', '-revoked_at'], name='users_revoke_user_id_revoked_idx'),
        ),
    ]
