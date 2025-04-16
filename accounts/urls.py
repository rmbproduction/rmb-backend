# accounts/urls.py
from django.urls import path
from .views import (
    GoogleLoginView,
    GoogleCallbackView,
    SignupView,
    LoginView,
    VerifyEmailView,
    LogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    rate_limit_view
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # Authentication URLs
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Email Verification
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    
    # Password Reset
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Google OAuth
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    
    # JWT Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Error Handling
    path('rate-limit/', rate_limit_view, name='rate-limit'),
]