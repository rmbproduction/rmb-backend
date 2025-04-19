from rest_framework import serializers
from .models import VehicleType, Manufacturer, VehicleModel, UserVehicle
from accounts.models import UserProfile

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ('id', 'name', 'image')  # You can also add more fields if required

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ('id', 'name', 'image')

class VehicleModelSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer()
    vehicle_type = VehicleTypeSerializer()

    class Meta:
        model = VehicleModel
        fields = ('id', 'name', 'manufacturer', 'vehicle_type', 'image')

class UserVehicleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    vehicle_type = VehicleTypeSerializer()
    manufacturer = ManufacturerSerializer()
    model = VehicleModelSerializer()

    class Meta:
        model = UserVehicle
        fields = ('id', 'user', 'vehicle_type', 'manufacturer', 'model', 'registration_number', 'purchase_date', 'vehicle_image')
