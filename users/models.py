from django.db import models
from django.contrib.auth.models import User
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class UserLoginHistory(models.Model):
    """Modelo para rastrear histórico de login de usuários"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_successful = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.login_time}'


class RevokedToken(models.Model):
    """Modelo para revogar tokens JWT de forma granular"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revoked_tokens')
    token_id = models.CharField(max_length=255, unique=True)  # jti claim do JWT
    revoked_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(
        max_length=50,
        choices=[
            ('logout', 'Logout voluntário'),
            ('password_change', 'Senha alterada'),
            ('account_disabled', 'Conta desativada'),
            ('suspicious_activity', 'Atividade suspeita'),
            ('admin_revoke', 'Revogação administrativa'),
        ],
        default='logout'
    )
    
    class Meta:
        ordering = ['-revoked_at']
        indexes = [
            models.Index(fields=['token_id']),
            models.Index(fields=['user', '-revoked_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - Token revogado em {self.revoked_at}'
