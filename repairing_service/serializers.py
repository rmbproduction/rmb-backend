from rest_framework import serializers
from .models import (
    Manufacturer, VehicleModel, Service, ServicePrice,
    ServiceCategory, Feature, Cart, CartItem
)
from vehicle.models import *

class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = '__all__'


class ServicePriceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    vehicle_model_name = serializers.CharField(source='vehicles_model.name', read_only=True)

    class Meta:
        model = ServicePrice
        fields = ['uuid', 'service_name', 'manufacturer_name', 'vehicle_model_name', 'price']


class ServiceSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = '__all__'


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['uuid', 'name']



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    vehicle_model_name = serializers.CharField(source="vehicle_model.name", read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'service', 'service_name', 'manufacturer', 'manufacturer_name', 'vehicle_model', 'vehicle_model_name', 'quantity']

