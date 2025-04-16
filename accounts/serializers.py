# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# Add this LoginSerializer class
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})



# accounts/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_active'] = user.is_active
        token['email_verified'] = user.email_verified
        token['date_joined'] = str(user.date_joined)
        
        return token

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['is_active'] = user.is_active
    refresh['email_verified'] = user.email_verified
    refresh['date_joined'] = str(user.date_joined)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Enter your registered email address",
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please enter a valid email address'
        }
    )

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            # We don't want to reveal if the email exists or not
            return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Enter your new password (minimum 8 characters)"
    )

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Enter your refresh token to logout",
        style={
            'base_template': 'textarea.html',
            'placeholder': 'Paste your refresh token here',
            'rows': 3,
            'cols': 40
        }
    )