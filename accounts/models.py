from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string  # Add this import at the top
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(64)
        super().save(*args, **kwargs)


