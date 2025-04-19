from django.contrib import admin
from .models import VehicleType, Manufacturer, VehicleModel, UserVehicle
from accounts.models import UserProfile

# VehicleType Admin Configuration
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)
    list_filter = ('name',)

# Manufacturer Admin Configuration
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = 10

# VehicleModel Admin Configuration
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'vehicle_type', 'image')
    search_fields = ('name', 'manufacturer__name', 'vehicle_type__name')
    list_filter = ('manufacturer', 'vehicle_type')
    list_per_page = 10

# UserVehicle Admin Configuration
class UserVehicleAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'manufacturer', 'model', 'registration_number', 'purchase_date', 'vehicle_image')
    search_fields = ('user__email', 'registration_number', 'model__name', 'manufacturer__name')
    list_filter = ('vehicle_type', 'manufacturer', 'model')
    list_per_page = 10

# Register Models with Admin
admin.site.register(VehicleType, VehicleTypeAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(VehicleModel, VehicleModelAdmin)
admin.site.register(UserVehicle, UserVehicleAdmin)
