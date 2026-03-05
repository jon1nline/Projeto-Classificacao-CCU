from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import jwt
from django.conf import settings
import logging

from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    UserSerializer,
    ChangePasswordSerializer
)
from .models import UserLoginHistory, RevokedToken

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para obter tokens JWT no login"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Override do post para registrar login"""
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                # Registra login bem-sucedido
                UserLoginHistory.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_successful=True
                )
                logger.info(f'Login bem-sucedido: {username} de {ip_address}')
            except User.DoesNotExist:
                pass
        else:
            # Registra tentativa falhada
            username = request.data.get('username')
            if username:
                try:
                    user = User.objects.get(username=username)
                    UserLoginHistory.objects.create(
                        user=user,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        is_successful=False
                    )
                except User.DoesNotExist:
                    pass
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Obtém IP do cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenRefreshView(TokenRefreshView):
    """View customizada para refrescar tokens"""
    serializer_class = TokenRefreshSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration_view(request):
    """Endpoint para registrar novo usuário"""
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f'Novo usuário registrado: {user.username}')
            
            # Gera tokens para novo usuário
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Usuário registrado com sucesso!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Endpoint para fazer logout (revoga refresh token)"""
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'success': False,
                'error': 'Refresh token não fornecido.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decodifica o token para obter o jti (token ID)
        try:
            decoded_token = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            token_id = decoded_token.get('jti')
            
            if token_id:
                # Revoga o token
                RevokedToken.objects.create(
                    user=request.user,
                    token_id=token_id,
                    reason='logout'
                )
            
            # Também adiciona à blacklist se configurado
            try:
                from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
                token = OutstandingToken.objects.get(jti=token_id)
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                pass
            
            logger.info(f'Logout bem-sucedido: {request.user.username}')
            
            return Response({
                'success': True,
                'message': 'Logout realizado com sucesso!'
            }, status=status.HTTP_200_OK)
        
        except jwt.InvalidTokenError:
            return Response({
                'success': False,
                'error': 'Token inválido.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f'Erro durante logout: {str(e)}')
        return Response({
            'success': False,
            'error': 'Erro ao fazer logout.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """Endpoint para obter perfil do usuário autenticado"""
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile_view(request):
    """Endpoint para atualizar perfil do usuário"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Perfil atualizado: {request.user.username}')
        return Response({
            'success': True,
            'message': 'Perfil atualizado com sucesso!',
            'user': serializer.data
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Endpoint para trocar senha"""
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Senha alterada: {request.user.username}')
        
        # Revoga todos os tokens anteriores por segurança
        RevokedToken.objects.create(
            user=request.user,
            token_id='all',  # Marca como revogação em massa
            reason='password_change'
        )
        
        return Response({
            'success': True,
            'message': 'Senha alterada com sucesso! Por favor, faça login novamente.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def login_history_view(request):
    """Endpoint para obter histórico de login do usuário"""
    history = UserLoginHistory.objects.filter(user=request.user)[:20]
    
    data = []
    for entry in history:
        data.append({
            'id': entry.id,
            'ip_address': entry.ip_address,
            'login_time': entry.login_time,
            'logout_time': entry.logout_time,
            'is_successful': entry.is_successful,
        })
    
    return Response({
        'success': True,
        'login_history': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_devices_view(request):
    """Endpoint para fazer logout em todos os dispositivos"""
    try:
        # Revoga todos os tokens do usuário
        RevokedToken.objects.create(
            user=request.user,
            token_id='all',
            reason='logout'
        )
        
        logger.info(f'Logout em todos os dispositivos: {request.user.username}')
        
        return Response({
            'success': True,
            'message': 'Logout realizado em todos os dispositivos!'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f'Erro ao fazer logout em todos os dispositivos: {str(e)}')
        return Response({
            'success': False,
            'error': 'Erro ao fazer logout.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
