"""
Testes para endpoints JWT e autenticação
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json
import logging

logger = logging.getLogger(__name__)


class JWTRegistrationTestCase(APITestCase):
    """Testes para registro de usuários via JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/'
    
    def test_valid_registration(self):
        """Testa registro com dados válidos"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_registration_with_short_password(self):
        """Testa rejeição de senha curta"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short',
            'password_confirm': 'short'
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
    
    def test_registration_with_existing_username(self):
        """Testa rejeição de username duplicado"""
        User.objects.create_user(username='existing', email='existing@test.com', password='pass123')
        
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
    
    def test_registration_password_mismatch(self):
        """Testa rejeição quando senhas não coincidem"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123',
            'password_confirm': 'differentpass'
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 400)


class JWTLoginTestCase(APITestCase):
    """Testes para login via JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/token/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_valid_login(self):
        """Testa login com credenciais válidas"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_with_wrong_password(self):
        """Testa login com senha incorreta"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, 401)
    
    def test_login_with_nonexistent_user(self):
        """Testa login com usuário que não existe"""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, 401)


class JWTRefreshTestCase(APITestCase):
    """Testes para refresh de tokens"""
    
    def setUp(self):
        self.client = APIClient()
        self.refresh_url = '/api/token/refresh/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Gera tokens iniciais
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)
    
    def test_valid_token_refresh(self):
        """Testa refresh válido de token"""
        data = {'refresh': self.refresh_token}
        response = self.client.post(self.refresh_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
    
    def test_refresh_with_invalid_token(self):
        """Testa refresh com token inválido"""
        data = {'refresh': 'invalid.token.here'}
        response = self.client.post(self.refresh_url, data)
        
        self.assertEqual(response.status_code, 401)


class JWTLogoutTestCase(APITestCase):
    """Testes para logout"""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = '/api/logout/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Gera tokens
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)
    
    def test_valid_logout(self):
        """Testa logout válido"""
        data = {'refresh': self.refresh_token}
        
        # Autentica com access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
    
    def test_logout_without_refresh_token(self):
        """Testa logout sem refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, {})
        
        self.assertEqual(response.status_code, 400)


class JWTProtectedEndpointsTestCase(APITestCase):
    """Testes para endpoints protegidos com JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/profile/'
        self.change_password_url = '/api/change-password/'
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_access_protected_endpoint_with_valid_token(self):
        """Testa acesso a endpoint protegido com token válido"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
    
    def test_access_protected_endpoint_without_token(self):
        """Testa acesso negado a endpoint protegido sem token"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 401)
    
    def test_change_password(self):
        """Testa mudança de senha"""
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
        # Verifica que a nova senha funciona
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))


class JWTSecurityTestCase(APITestCase):
    """Testes de segurança para JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/token/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_token_expiration(self):
        """Verifica que tokens têm tempo de expiração configurado"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        # Decodifica o token para verificar 'exp' claim
        import jwt
        from django.conf import settings
        
        access_token = response.data['access']
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        
        self.assertIn('exp', decoded)
        self.assertIn('iat', decoded)
    
    def test_rate_limiting_on_login(self):
        """Testa rate limiting em múltiplas tentativas de login"""
        # Fazemos múltiplas tentativas de login falhadas
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        attempts = 0
        for i in range(10):
            response = self.client.post(self.login_url, data)
            if response.status_code == 429:
                logger.info(f'Rate limit atingido após {i+1} tentativas')
                break
            attempts += 1
        
        # Verifica que rate limit foi aplicado
        self.assertGreater(9, attempts)
    
    def test_security_headers(self):
        """Verifica que headers de segurança são adicionados"""
        response = self.client.get('/')
        
        self.assertEqual(response.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.get('X-Frame-Options'), 'DENY')
        self.assertIn('Strict-Transport-Security', response)


class JWTIntegrationTestCase(APITestCase):
    """Testes de integração do fluxo completo de autenticação"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/'
        self.login_url = '/api/token/'
        self.logout_url = '/api/logout/'
        self.profile_url = '/api/profile/'
    
    def test_complete_auth_flow(self):
        """Testa fluxo completo: registro -> login -> acesso -> logout"""
        
        # 1. Registro
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepwd123',
            'password_confirm': 'securepwd123'
        }
        register_response = self.client.post(self.register_url, register_data)
        self.assertEqual(register_response.status_code, 201)
        
        # 2. Login
        login_data = {
            'username': 'newuser',
            'password': 'securepwd123'
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, 200)
        
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # 3. Acesso a endpoint protegido
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, 200)
        
        # 4. Logout
        logout_data = {'refresh': refresh_token}
        logout_response = self.client.post(self.logout_url, logout_data)
        self.assertEqual(logout_response.status_code, 200)
