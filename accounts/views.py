import os
import requests
import logging
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings
from decouple import config 
from django.utils.crypto import get_random_string
from django.core.cache import cache
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.core.mail import send_mail
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, EmailVerificationToken
from .serializers import (
    UserSerializer, 
    LoginSerializer, 
    LogoutSerializer, 
    PasswordResetSerializer, 
    PasswordResetConfirmSerializer, 
    get_tokens_for_user
)
import jwt
from rest_framework.permissions import AllowAny
from collections import defaultdict
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# Google OAuth settings
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "http://localhost:8000/api/accounts/google/callback/"

# Simple rate limiting
request_counts = defaultdict(list)

def check_rate_limit(ip, limit=5, window=60):
    """
    Check if the IP has exceeded the rate limit.
    limit: maximum number of requests
    window: time window in seconds
    """
    now = datetime.now()
    request_times = request_counts[ip]
    
    # Remove old requests
    request_times = [time for time in request_times if (now - time).total_seconds() < window]
    request_counts[ip] = request_times
    
    # Check if limit is exceeded
    if len(request_times) >= limit:
        return True
    
    # Add current request
    request_times.append(now)
    return False

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one number")
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        raise ValidationError("Password must contain at least one special character")

def check_login_attempts(email):
    """Check and manage login attempts"""
    attempts = cache.get(f'login_attempts_{email}', 0)
    if attempts >= 5:
        lockout_time = cache.get(f'account_lockout_{email}')
        if lockout_time:
            remaining_time = (lockout_time - timezone.now()).total_seconds()
            if remaining_time > 0:
                raise ValidationError(f"Account locked. Please try again in {int(remaining_time/60)} minutes.")
            else:
                cache.delete(f'account_lockout_{email}')
                cache.delete(f'login_attempts_{email}')
        else:
            cache.set(f'account_lockout_{email}', timezone.now() + timezone.timedelta(minutes=30), timeout=1800)
            raise ValidationError("Account locked for 30 minutes due to too many failed attempts.")

class PasswordResetView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    @method_decorator(ratelimit(key='ip', rate='3/h', method=['POST']))
    def post(self, request):
        if getattr(request, 'limited', False):
            return Response({
                "error": "Too many password reset attempts. Please try again later.",
                "detail": "Rate limit exceeded"
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        
        # Check rate limiting for reset attempts
        reset_attempts = cache.get(f'reset_attempts_{email}', 0)
        if reset_attempts >= 3:
            return Response({
                "message": "Too many reset attempts. Please try again later."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            user = User.objects.get(email=email)
            # Generate reset token
            token = get_random_string(64)
            cache.set(f'password_reset_{token}', user.pk, timeout=3600)  # 1 hour expiry

            # Create reset URL
            reset_url = request.build_absolute_uri(
                f'/api/accounts/password-reset/{token}/'
            )

            # Send reset email
            send_mail(
                subject="Password Reset Request",
                message=f"Click this link to reset your password:\n\n{reset_url}\n\nThis link will expire in 1 hour.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Increment reset attempts
            cache.set(f'reset_attempts_{email}', reset_attempts + 1, timeout=3600)
            
            # Log the reset request
            logger.info(f"Password reset requested for {email}")

            return Response({
                "message": "Password reset email sent. Please check your email."
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({
                "message": "If an account exists with this email, you will receive a password reset link."
            }, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetConfirmSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['password']

        # Validate password strength
        try:
            validate_password_strength(new_password)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Get user from cache
        user_id = cache.get(f'password_reset_{token}')
        if not user_id:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
            
            # Check if password was recently used
            if user.check_password(new_password):
                return Response(
                    {"error": "This password was recently used. Please choose a different one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            # Delete the token from cache
            cache.delete(f'password_reset_{token}')
            
            # Log the password reset
            logger.info(f"Password reset successful for user {user.email}")

            return Response({
                "message": "Password has been reset successfully"
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    @method_decorator(ratelimit(key='ip', rate='5/m', method=['POST']))
    def post(self, request):
        try:
            if getattr(request, 'limited', False):
                return Response({
                    "error": "Too many login attempts. Please try again later.",
                    "detail": "Rate limit exceeded"
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Try to check login attempts, but don't fail if cache is down
            try:
                check_login_attempts(email)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except Exception as e:
                # Log the error but continue with authentication
                logger.error(f"Error checking login attempts: {str(e)}")

            # First check if user exists but is not verified
            try:
                user_exists = User.objects.filter(email=email).exists()
                user_obj = User.objects.get(email=email) if user_exists else None
                
                if user_exists and not user_obj.is_active:
                    return Response({
                        "error": "Please verify your email before logging in",
                        "email_verification_required": True,
                        "email": email
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                logger.error(f"Error checking user verification status: {str(e)}")

            # Authenticate user
            user = authenticate(request, email=email, password=password)
            
            if not user:
                # Try to increment failed login attempts, but don't fail if cache is down
                try:
                    attempts = cache.get(f'login_attempts_{email}', 0)
                    cache.set(f'login_attempts_{email}', attempts + 1, timeout=3600)
                except Exception as e:
                    logger.error(f"Error tracking failed login attempts: {str(e)}")
                
                # Log failed attempt
                logger.warning(f"Failed login attempt for {email}")
                
                return Response({
                    "error": "Invalid credentials"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Reset login attempts on successful login
            try:
                cache.delete(f'login_attempts_{email}')
                cache.delete(f'account_lockout_{email}')
            except Exception as e:
                logger.error(f"Error clearing login attempts: {str(e)}")
            
            # Log successful login
            logger.info(f"Successful login for {email}")

            # Get tokens with custom claims
            try:
                tokens = get_tokens_for_user(user)
                
                # Check if this is first login after verification
                is_first_login = user.last_login is None
                
                # Update last login time
                if is_first_login:
                    logger.info(f"First login after verification for {email}")
                
                return Response({
                    "message": "Login successful",
                    "is_first_login": is_first_login,
                    "tokens": tokens,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "email_verified": user.email_verified
                    }
                })
            except Exception as e:
                logger.error(f"Error generating tokens: {str(e)}")
                return Response({
                    "error": "Authentication successful but failed to generate tokens. Please try again."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected login error: {str(e)}")
            return Response({
                "error": "An unexpected error occurred. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
@login_required
def success_page(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    
    return render(request, 'success.html', {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': user,
    })

def rate_limit_view(request, exception):
    """View to handle rate limit exceeded responses"""
    return Response(
        {
            "error": "Rate limit exceeded. Please try again later.",
            "detail": "You have made too many requests. Please wait before trying again."
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS
    )

class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={GOOGLE_REDIRECT_URI}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile"
        )
        return Response({"auth_url": url})

class GoogleCallbackView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Exchange code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")

            # Get user info from Google
            user_info = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ).json()

            email = user_info.get("email")
            if not email:
                return Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': user_info.get('name', email.split('@')[0]),
                    'is_active': True,
                    'email_verified': True
                }
            )

            if created:
                user.set_unusable_password()
                user.save()

            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            
            return Response({
                "message": "Login successful",
                "tokens": tokens,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"Google OAuth error: {str(e)}")
            return Response(
                {"error": "Failed to authenticate with Google"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error during Google authentication: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SignupView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    @method_decorator(csrf_exempt)
    @method_decorator(ratelimit(key='ip', rate='20/h', method=['POST']))
    def post(self, request):
        if getattr(request, 'limited', False):
            return Response({
                "error": "Too many signup attempts. Please try again later.",
                "detail": "Rate limit exceeded"
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "error": "User with this email already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        try:
            validate_password_strength(password)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create user account (inactive until email is verified)
        user = serializer.save()
        user.is_active = False  # Disable until email verification
        user.save()
        
        # Generate verification token
        token = get_random_string(64)
        
        # Store in both cache and database for redundancy
        try:
            # Store in cache with 24 hour expiry
            cache.set(f'email_verification_{token}', user.pk, timeout=86400)
            
            # Also store in database
            EmailVerificationToken.objects.create(
                user=user,
                token=token
            )
            
            # Generate verification URL
            verification_url = request.build_absolute_uri(
                f'/api/accounts/verify-email/{token}/'
            )
            
            # Send verification email
            send_mail(
                subject="Verify Your Email",
                message=f"Thank you for signing up! Please click the link below to verify your email:\n\n{verification_url}\n\nThis link will expire in 24 hours.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            # Log signup
            logger.info(f"New user signed up: {email}")
            
            return Response({
                "message": "Registration successful! Please check your email to verify your account.",
                "email": email,
                "verification_required": True,
                "next_step": "Please verify your email before logging in. Check your inbox for a verification link."
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If email sending fails, delete the user and return error
            user.delete()
            logger.error(f"Signup error: {str(e)}")
            return Response({
                "error": "Failed to create account. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token):
        try:
            # Try to get user_id from cache first
            user_id = cache.get(f'email_verification_{token}')
            
            if not user_id:
                # If not in cache, check if token exists in database
                verification_token = EmailVerificationToken.objects.filter(
                    token=token,
                    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
                ).first()
                
                if verification_token:
                    user_id = verification_token.user.id
                else:
                    return Response({
                        "error": "Invalid or expired verification link"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(pk=user_id)
                if not user.is_active:
                    user.is_active = True
                    user.email_verified = True
                    user.save()
                    
                    try:
                        # Try to clear verification token from cache
                        cache.delete(f'email_verification_{token}')
                        # Also delete from database if it exists
                        EmailVerificationToken.objects.filter(token=token).delete()
                    except Exception as e:
                        logger.warning(f"Failed to delete verification token: {str(e)}")
                    
                    logger.info(f"Email verified for user: {user.email}")
                    
                    return Response({
                        "message": "Email verified successfully. You can now log in with your credentials.",
                        "verified": True,
                        "user": {
                            "email": user.email,
                        }
                    }, status=status.HTTP_200_OK)
                
                return Response({
                    "message": "Email already verified. You can log in with your credentials.",
                    "verified": True,
                    "user": {
                        "email": user.email,
                    }
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                logger.error(f"Verification failed: User not found for token {token}")
                return Response({
                    "error": "User not found"
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return Response({
                "error": "An error occurred during email verification"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            refresh_token = serializer.validated_data['refresh']

            # Blacklist the refresh token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                # Try to log the logout if user is authenticated
                if request.user.is_authenticated:
                    logger.info(f"User {request.user.email} logged out successfully")
                else:
                    logger.info("User logged out successfully (unauthenticated)")

                return Response(
                    {"message": "Successfully logged out"},
                    status=status.HTTP_200_OK
                )
            except TokenError as e:
                return Response(
                    {"error": "Invalid token. Please provide a valid refresh token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": "An error occurred during logout"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from django.http import JsonResponse

def accounts_root_view(request):
    return JsonResponse({"message": "Welcome to the Accounts API!"})