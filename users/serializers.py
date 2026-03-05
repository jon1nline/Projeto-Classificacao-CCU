from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários com validação"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate_username(self, value):
        """Verifica se username já existe"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este usuário já exists.')
        return value
    
    def validate_email(self, value):
        """Verifica se email já existe"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email já está registrado.')
        return value
    
    def validate(self, data):
        """Valida se as senhas coincidem"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password': 'As senhas não coincidem.'})
        
        if len(data.get('password', '')) < 8:
            raise serializers.ValidationError({'password': 'A senha deve ter no mínimo 8 caracteres.'})
        
        return data
    
    def create(self, validated_data):
        """Cria novo usuário com a senha hasheada"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer customizado para login JWT"""
    
    def validate(self, attrs):
        """Override para melhorar validação do login"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Tenta autenticar o usuário
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError(
                'Usuário ou senha incorretos.',
                code='authentication'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                'Esta conta está desativada.',
                code='inactive'
            )
        
        # Gera tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer para refrescar access token"""
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        """Valida o refresh token"""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            RefreshToken(value)
        except Exception:
            raise serializers.ValidationError('Token de refresh inválido ou expirado.')
        return value


class LogoutSerializer(serializers.Serializer):
    """Serializer para logout (blacklist do refresh token)"""
    refresh = serializers.CharField(required=True)
    
    def validate_refresh(self, value):
        """Valida o refresh token antes de fazer logout"""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(value)
            # Token será blacklisted se blacklist app estiver configurado
            return value
        except Exception:
            raise serializers.ValidationError('Token inválido.')


class UserSerializer(serializers.ModelSerializer):
    """Serializer para dados do usuário"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id', 'is_active']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para trocar senha"""
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Valida senhas"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'new_password': 'As senhas não coincidem.'})
        
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError({'new_password': 'A nova senha deve ser diferente da atual.'})
        
        return data
    
    def validate_old_password(self, value):
        """Valida a senha antiga"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value
    
    def save(self, **kwargs):
        """Salva a nova senha"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
