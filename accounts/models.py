from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Add related_name for groups and user_permissions to avoid clash with default User model
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set',  # Custom reverse relation name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_permission_set',  # Custom reverse relation name
        blank=True
    )

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        return self.created_at >= timezone.now() - timezone.timedelta(hours=24)

    @classmethod
    def generate_token(cls, user):
        token = get_random_string(64)
        return cls.objects.create(user=user, token=token)


class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    address = models.TextField()
    profile_photo = models.ImageField(upload_to="profiles/")
    vehicle_name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)

    def __str__(self):
        return self.email
