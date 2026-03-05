from django.urls import path
from . import views
from .jwt_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    user_registration_view,
    logout_view as jwt_logout_view,
    user_profile_view,
    update_user_profile_view,
    change_password_view,
    login_history_view,
    logout_all_devices_view,
)

urlpatterns = [
    # Views tradicionais (compatibilidade)
    path('registro/', views.registro, name='registro'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Endpoints JWT (API REST)
    path('api/register/', user_registration_view, name='api_register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='api_token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/logout/', jwt_logout_view, name='api_logout'),
    path('api/profile/', user_profile_view, name='api_profile'),
    path('api/profile/update/', update_user_profile_view, name='api_profile_update'),
    path('api/change-password/', change_password_view, name='api_change_password'),
    path('api/login-history/', login_history_view, name='api_login_history'),
    path('api/logout-all-devices/', logout_all_devices_view, name='api_logout_all_devices'),
]
