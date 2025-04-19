from rest_framework import serializers
from django.utils import timezone
from django.core.validators import RegexValidator
from .models import Vehicle, SellRequest, InspectionReport, PurchaseOffer, VehiclePurchase

class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model with validation"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    short_description = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    condition_rating = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_type', 'brand', 'model', 'year', 'registration_number',
            'kms_driven', 'fuel_type', 'engine_capacity', 'color',
            'last_service_date', 'insurance_valid_till', 'status', 'status_display',
            'short_description', 'display_price', 'image_urls', 'features',
            'condition_rating'
        ]
        read_only_fields = ['status', 'status_display']

    def get_short_description(self, obj):
        return f"{obj.year} {obj.brand} {obj.model} - {obj.kms_driven:,} km | {obj.fuel_type}"

    def get_display_price(self, obj):
        # You would typically have a price field in your Vehicle model
        # For now, we'll return a placeholder
        return {
            'amount': 0,  # Replace with actual price
            'currency': 'INR',
            'formatted': '₹0',  # Replace with actual formatted price
            'emi_available': True,  # Add logic for EMI availability
            'emi_starting_at': '₹0/month'  # Add EMI calculation
        }

    def get_image_urls(self, obj):
        # Replace with actual image URLs from your model
        return {
            'thumbnail': None,
            'main': None,
            'gallery': []
        }

    def get_features(self, obj):
        features = []
        if obj.engine_capacity:
            features.append(f"{obj.engine_capacity}cc Engine")
        if obj.fuel_type:
            features.append(f"{obj.fuel_type} Powered")
        if obj.last_service_date:
            features.append("Recently Serviced")
        if obj.insurance_valid_till:
            features.append("Insurance Valid")
        return features

    def get_condition_rating(self, obj):
        # Get condition rating from inspection report if available
        try:
            if hasattr(obj, 'sell_request') and obj.sell_request.inspection_report:
                return {
                    'score': obj.sell_request.inspection_report.overall_rating,
                    'max_score': 5,
                    'label': obj.sell_request.inspection_report.get_overall_rating_display()
                }
        except:
            pass
        return None

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError("Year cannot be in the future")
        if value < 1900:
            raise serializers.ValidationError("Year cannot be before 1900")
        return value

    def validate_registration_number(self, value):
        if not value:
            raise serializers.ValidationError("Registration number is required")
        # Add your registration number format validation here
        return value.upper()

class InspectionReportSerializer(serializers.ModelSerializer):
    """Serializer for inspection reports with computed fields"""
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)
    condition_summary = serializers.SerializerMethodField()

    class Meta:
        model = InspectionReport
        fields = [
            'id', 'sell_request', 'inspector', 'inspector_name',
            'engine_condition', 'transmission_condition', 'suspension_condition',
            'tyre_condition', 'brake_condition', 'electrical_condition',
            'frame_condition', 'paint_condition', 'overall_rating',
            'estimated_repair_cost', 'remarks', 'inspection_photos',
            'passed', 'condition_summary', 'created_at'
        ]
        read_only_fields = ['overall_rating', 'passed']

    def get_condition_summary(self, obj):
        return {
            'mechanical': {
                'engine': obj.engine_condition,
                'transmission': obj.transmission_condition,
                'suspension': obj.suspension_condition,
                'brakes': obj.brake_condition,
                'electrical': obj.electrical_condition,
            },
            'cosmetic': {
                'frame': obj.frame_condition,
                'paint': obj.paint_condition,
                'tyres': obj.tyre_condition,
            },
            'overall': obj.overall_rating,
            'verdict': 'Pass' if obj.passed else 'Fail'
        }

class SellRequestSerializer(serializers.ModelSerializer):
    """Serializer for sell requests with nested vehicle details"""
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    inspection_details = InspectionReportSerializer(source='inspection_report', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    documents_complete = serializers.SerializerMethodField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    contact_number = serializers.CharField(validators=[phone_regex], required=True)

    class Meta:
        model = SellRequest
        fields = [
            'id', 'user', 'vehicle', 'vehicle_details', 'documents',
            'photos', 'pickup_slot', 'pickup_address', 'contact_number',
            'status', 'status_display', 'rejection_reason', 'documents_complete',
            'inspection_details', 'created_at'
        ]
        read_only_fields = ['user', 'status']

    def get_documents_complete(self, obj):
        required_docs = {'rc', 'insurance', 'puc'}
        submitted_docs = set(obj.documents.keys() if obj.documents else {})
        return {
            'complete': required_docs.issubset(submitted_docs),
            'missing': list(required_docs - submitted_docs)
        }

    def validate_pickup_slot(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Pickup slot cannot be in the past")
        # Ensure pickup slot is during business hours (9 AM to 6 PM)
        if value and (value.hour < 9 or value.hour >= 18):
            raise serializers.ValidationError("Pickup slot must be between 9 AM and 6 PM")
        return value

    def validate_photos(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Photos must be a list")
        required_views = {'front', 'back', 'left', 'right'}
        submitted_views = {photo.get('view', '').lower() for photo in value if isinstance(photo, dict)}
        missing = required_views - submitted_views
        if missing:
            raise serializers.ValidationError(f"Missing required photo views: {', '.join(missing)}")
        return value

    def validate_documents(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Documents must be a dictionary")
        required_docs = {'rc', 'insurance', 'puc'}
        submitted_docs = set(value.keys())
        missing = required_docs - submitted_docs
        if missing:
            raise serializers.ValidationError(f"Missing required documents: {', '.join(missing)}")
        return value

    def validate_pickup_address(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete pickup address (minimum 10 characters)")
        return value.strip()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class PurchaseOfferSerializer(serializers.ModelSerializer):
    """Serializer for purchase offers with price validation"""
    sell_request_details = SellRequestSerializer(source='sell_request', read_only=True)
    valid_until_display = serializers.SerializerMethodField()
    price_analysis = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOffer
        fields = [
            'id', 'sell_request', 'sell_request_details', 'market_value',
            'offer_price', 'price_breakdown', 'is_negotiable', 'accepted',
            'counter_offer', 'valid_until', 'valid_until_display',
            'price_analysis', 'created_at'
        ]
        read_only_fields = ['valid_until']

    def get_valid_until_display(self, obj):
        if not obj.valid_until:
            return None
        return {
            'date': obj.valid_until.date(),
            'time': obj.valid_until.time(),
            'expired': obj.valid_until < timezone.now()
        }

    def get_price_analysis(self, obj):
        if not obj.price_breakdown:
            return None
        
        base_price = obj.price_breakdown.get('base_price', 0)
        deductions = obj.price_breakdown.get('deductions', {})
        total_deductions = sum(deductions.values())
        
        return {
            'base_price': base_price,
            'deductions': deductions,
            'total_deductions': total_deductions,
            'final_price': base_price + total_deductions,
            'market_difference': obj.market_value - obj.offer_price if obj.market_value else None
        }

    def validate(self, data):
        if data.get('offer_price', 0) <= 0:
            raise serializers.ValidationError({"offer_price": "Offer price must be greater than zero"})
        if data.get('counter_offer') is not None and data['counter_offer'] <= 0:
            raise serializers.ValidationError({"counter_offer": "Counter offer must be greater than zero"})
        return data

class VehiclePurchaseSerializer(serializers.ModelSerializer):
    """Serializer for handling vehicle purchases"""
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    contact_number = serializers.CharField(validators=[phone_regex])

    class Meta:
        model = VehiclePurchase
        fields = [
            'id', 'vehicle', 'vehicle_details', 'buyer', 'amount',
            'status', 'status_display', 'payment_method', 'purchase_date',
            'completion_date', 'delivery_address', 'contact_number',
            'notes', 'payment_id'
        ]
        read_only_fields = ['buyer', 'status', 'purchase_date', 'completion_date', 'payment_id']

    def validate_vehicle(self, value):
        if value.status != 'available':
            raise serializers.ValidationError("This vehicle is not available for purchase")
        return value

    def validate_delivery_address(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete delivery address (minimum 10 characters)")
        return value.strip()

    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        validated_data['status'] = VehiclePurchase.Status.PENDING
        return super().create(validated_data)