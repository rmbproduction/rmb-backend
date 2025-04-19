# admin.py
from django.contrib import admin
from .models import Feature, ServiceCategory, Service, ServicePrice, Cart, CartItem
from vehicle.models import Manufacturer, VehicleModel

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('name',)



class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'discounted_price', 'duration', 'warranty', 'recommended')
    list_filter = ('category', 'manufacturers', 'vehicles_models')  # Changed to vehicles_models
    search_fields = ('name', 'description')
    filter_horizontal = ('manufacturers', 'vehicles_models', 'features')  # Changed to vehicles_models



class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ('service', 'manufacturer', 'vehicles_model', 'price')
    list_filter = ('service', 'manufacturer', 'vehicles_model')
    search_fields = ('service__name', 'manufacturer__name', 'vehicles_model__name')

    def vehicles_model(self, obj):
        return obj.vehicles_model.name if obj.vehicles_model else "N/A"

    vehicles_model.admin_order_field = 'vehicles_model__name'





class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_service_count')
    search_fields = ('user__email',)

    def get_service_count(self, obj):
        return obj.services.count()
    get_service_count.short_description = 'Service Count'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'service', 'quantity')
    search_fields = ('cart__user__email', 'service__name')

# Register your models here
admin.site.register(Feature, FeatureAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServicePrice, ServicePriceAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)









