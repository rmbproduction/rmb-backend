from django.contrib import admin
from .models import Vehicle, SellRequest, InspectionReport, PurchaseOffer

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'vehicle_type', 'brand', 'model', 'year', 'status', 'fuel_type')
    list_filter = ('vehicle_type', 'status', 'fuel_type', 'brand')
    search_fields = ('registration_number', 'brand', 'model')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('vehicle_type', 'brand', 'model', 'year', 'registration_number', 'owner')
        }),
        ('Specifications', {
            'fields': ('fuel_type', 'engine_capacity', 'kms_driven', 'color')
        }),
        ('Documents & Service', {
            'fields': ('last_service_date', 'insurance_valid_till')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )

@admin.register(SellRequest)
class SellRequestAdmin(admin.ModelAdmin):
    list_display = ('get_registration', 'user', 'status', 'pickup_slot', 'created_at')
    list_filter = ('status',)
    search_fields = ('vehicle__registration_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def get_registration(self, obj):
        return obj.vehicle.registration_number
    get_registration.short_description = 'Registration Number'

@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ('get_registration', 'inspector', 'overall_rating', 'passed', 'created_at')
    list_filter = ('passed', 'overall_rating')
    search_fields = ('sell_request__vehicle__registration_number',)
    readonly_fields = ('created_at', 'updated_at')

    def get_registration(self, obj):
        return obj.sell_request.vehicle.registration_number
    get_registration.short_description = 'Registration Number'

@admin.register(PurchaseOffer)
class PurchaseOfferAdmin(admin.ModelAdmin):
    list_display = ('get_registration', 'market_value', 'offer_price', 'accepted', 'valid_until')
    list_filter = ('accepted', 'is_negotiable')
    search_fields = ('sell_request__vehicle__registration_number',)
    readonly_fields = ('created_at', 'updated_at')

    def get_registration(self, obj):
        return obj.sell_request.vehicle.registration_number
    get_registration.short_description = 'Registration Number'
