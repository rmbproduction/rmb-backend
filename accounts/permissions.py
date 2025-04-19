from rest_framework.permissions import BasePermission

class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.owner == request.user  # Adjust as needed


from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['email', 'name', 'username', 'address', 'vehicle_name', 'vehicle_type', 'manufacturer']