"""
Middleware para validação e verificação de segurança de JWT tokens
"""
import jwt
import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from .models import RevokedToken

logger = logging.getLogger(__name__)


class JWTTokenValidationMiddleware:
    """
    Middleware para validar JWT tokens revogados
    Verifica se um token foi revogado na tabela RevokedToken
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processa somente requisições com token JWT
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer '
            
            try:
                # Decodifica o token para obter o jti
                decoded = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                
                token_id = decoded.get('jti')
                user_id = decoded.get('user_id')
                
                if token_id and user_id:
                    # Verifica se o token foi revogado
                    if self._is_token_revoked(token_id, user_id):
                        logger.warning(f'Tentativa de uso de token revogado: user_id={user_id}, jti={token_id}')
                        return JsonResponse(
                            {
                                'success': False,
                                'error': 'Token revogado. Por favor, faça login novamente.'
                            },
                            status=401
                        )
            
            except (jwt.InvalidTokenError, jwt.DecodeError) as e:
                logger.warning(f'Erro ao decodificar token JWT: {str(e)}')
                pass  # Deixa o DRF lidar com o erro
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def _is_token_revoked(token_id, user_id):
        """
        Verifica se um token foi revogado
        """
        try:
            # Verifica se há revogação em massa para o usuário
            if RevokedToken.objects.filter(user_id=user_id, token_id='all').exists():
                return True
            
            # Verifica se o token específico foi revogado
            if RevokedToken.objects.filter(token_id=token_id).exists():
                return True
            
            return False
        
        except Exception as e:
            logger.error(f'Erro ao verificar token revogado: {str(e)}')
            return False


class SecurityHeadersMiddleware:
    """
    Middleware para adicionar headers de segurança a respostas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Headers de segurança
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Restringe acesso ao conteúdo
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RateLimitMiddleware:
    """
    Middleware para rate limiting em endpoints de autenticação
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.failed_attempts = {}  # {ip: [(timestamp, count)]}
    
    def __call__(self, request):
        # Aplica rate limit a endpoints sensíveis
        if request.path in ['/api/token/', '/api/register/', '/api/logout/']:
            ip = self._get_client_ip(request)
            
            if self._is_rate_limited(ip):
                logger.warning(f'Rate limit atingido para IP: {ip}')
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'Muitas tentativas. Tente novamente mais tarde.'
                    },
                    status=429
                )
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Obtém IP do cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_rate_limited(self, ip, max_attempts=5, window_size=300):
        """
        Verifica se o IP excedeu o limite de requisições
        max_attempts: número máximo de tentativas
        window_size: tamanho da janela em segundos
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        # Remove tentativas antigas
        self.failed_attempts[ip] = [
            timestamp for timestamp in self.failed_attempts[ip]
            if timestamp > now - timedelta(seconds=window_size)
        ]
        
        # Adiciona tentativa atual
        self.failed_attempts[ip].append(now)
        
        # Verifica se excedeu limite
        return len(self.failed_attempts[ip]) > max_attempts
