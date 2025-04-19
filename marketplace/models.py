from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

User = settings.AUTH_USER_MODEL

def get_current_year():
    return timezone.now().year

def get_default_valid_until():
    return timezone.now() + timedelta(days=7)

class BaseModel(models.Model):
    """Base model with common timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class Vehicle(BaseModel):
    """
    Vehicle model representing any two-wheeler (bike, scooter, etc.)
    Handles both petrol and electric vehicles
    """
    class VehicleType(models.TextChoices):
        BIKE = 'bike', 'Bike'
        SCOOTER = 'scooter', 'Scooter'
        ELECTRIC_SCOOTER = 'electric_scooter', 'Electric Scooter'
        ELECTRIC_BIKE = 'electric_bike', 'Electric Bike'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        UNDER_INSPECTION = 'under_inspection', 'Under Inspection'
        INSPECTION_DONE = 'inspection_done', 'Inspection Done'
        SOLD = 'sold', 'Sold'

    class FuelType(models.TextChoices):
        PETROL = 'petrol', 'Petrol'
        ELECTRIC = 'electric', 'Electric'

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        help_text="Current owner of the vehicle"
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.BIKE,
        help_text="Type of two-wheeler"
    )
    brand = models.CharField(
        max_length=50,
        default='',
        blank=True,
        help_text="Vehicle manufacturer"
    )
    model = models.CharField(
        max_length=50,
        default='',
        blank=True,
        help_text="Vehicle model name"
    )
    year = models.PositiveIntegerField(
        default=get_current_year,
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(get_current_year)
        ],
        help_text="Manufacturing year"
    )
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        default='',
        blank=True,
        help_text="Vehicle registration number"
    )
    kms_driven = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total kilometers driven"
    )
    fuel_type = models.CharField(
        max_length=10,
        choices=FuelType.choices,
        default=FuelType.PETROL,
        help_text="Fuel type (petrol/electric)"
    )
    engine_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Engine capacity in CC (petrol) or Watts (electric)"
    )
    color = models.CharField(
        max_length=30,
        default='Not Specified',
        blank=True,
        help_text="Vehicle color"
    )
    last_service_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last service"
    )
    insurance_valid_till = models.DateField(
        null=True,
        blank=True,
        help_text="Insurance validity date"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNDER_INSPECTION,
        help_text="Current vehicle status"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Selling price of the vehicle"
    )
    emi_available = models.BooleanField(
        default=True,
        help_text="Whether EMI is available for this vehicle"
    )
    emi_months = models.JSONField(
        default=list,
        help_text="Available EMI tenures in months"
    )
    images = models.JSONField(
        default=dict,
        help_text='Format: {"thumbnail": "url", "main": "url", "gallery": ["url1", "url2"]}'
    )
    features = models.JSONField(
        default=list,
        help_text="List of vehicle features"
    )
    highlights = models.JSONField(
        default=list,
        help_text="Key highlights of the vehicle"
    )

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=['vehicle_type', 'brand', 'model']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['status']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.year} {self.brand or 'Unknown'} {self.model or 'Unknown'} - {self.registration_number}"

    def calculate_emi(self, months=12, interest_rate=10):
        """Calculate EMI for the vehicle"""
        if not self.emi_available or not self.price:
            return None
        
        principal = float(self.price)
        rate = interest_rate / (12 * 100)  # Monthly interest rate
        
        # EMI calculation formula
        emi = principal * rate * pow(1 + rate, months)
        emi = emi / (pow(1 + rate, months) - 1)
        
        return round(emi, 2)

class SellRequest(BaseModel):
    """
    Represents a request to sell a vehicle
    Tracks the entire selling process from submission to completion
    """
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        DOCUMENTS_VERIFIED = 'documents_verified', 'Documents Verified'
        PICKUP_SCHEDULED = 'pickup_scheduled', 'Pickup Scheduled'
        UNDER_INSPECTION = 'under_inspection', 'Under Inspection'
        INSPECTION_DONE = 'inspection_done', 'Inspection Done'
        OFFER_MADE = 'offer_made', 'Offer Made'
        DEAL_CLOSED = 'deal_closed', 'Deal Closed'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sell_requests',
        help_text="User who wants to sell the vehicle"
    )
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sell_request',
        help_text="Vehicle being sold"
    )
    documents = models.JSONField(
        default=dict,
        blank=True,
        help_text='Format: {"rc": "path", "insurance": "path", "puc": "path"}'
    )
    photos = models.JSONField(
        default=list,
        blank=True,
        help_text='List of photo paths: ["front_view", "back_view", etc.]'
    )
    pickup_slot = models.DateTimeField(
        default=timezone.now,
        help_text="Scheduled pickup time"
    )
    pickup_address = models.TextField(
        default='',
        blank=True,
        help_text="Address for vehicle pickup"
    )
    contact_number = models.CharField(
        max_length=15,
        default='',
        blank=True,
        help_text="Contact number for pickup"
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SUBMITTED,
        help_text="Current status of sell request"
    )
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason if request is rejected"
    )

    def __str__(self):
        return f"Sell Request - {self.vehicle.registration_number if self.vehicle else 'Unassigned'}"

class InspectionReport(BaseModel):
    """
    Detailed inspection report for a vehicle
    Includes mechanical and cosmetic condition assessment
    """
    class Condition(models.IntegerChoices):
        POOR = 1, 'Poor'
        BELOW_AVERAGE = 2, 'Below Average'
        AVERAGE = 3, 'Average'
        GOOD = 4, 'Good'
        EXCELLENT = 5, 'Excellent'

    sell_request = models.OneToOneField(
        SellRequest,
        on_delete=models.CASCADE,
        related_name='inspection_report',
        help_text="Related sell request"
    )
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
        help_text="Inspector who performed the inspection"
    )

    engine_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Engine condition rating"
    )
    transmission_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Transmission condition rating"
    )
    suspension_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Suspension condition rating"
    )
    tyre_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Tyre condition rating"
    )
    brake_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Brake system condition rating"
    )
    electrical_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Electrical system condition rating"
    )

    frame_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Frame condition rating"
    )
    paint_condition = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        help_text="Paint condition rating"
    )

    overall_rating = models.IntegerField(
        choices=Condition.choices,
        default=Condition.POOR,
        editable=False,
        help_text="Overall vehicle condition rating (auto-calculated)"
    )
    estimated_repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Estimated cost of repairs needed"
    )
    remarks = models.TextField(
        default='',
        blank=True,
        help_text="Additional inspection notes"
    )
    inspection_photos = models.JSONField(
        default=list,
        blank=True,
        help_text="List of inspection photo paths"
    )
    passed = models.BooleanField(
        default=False,
        editable=False,
        help_text="Whether vehicle passed inspection (auto-calculated)"
    )

    def save(self, *args, **kwargs):
        """Calculate overall rating and pass/fail status before saving"""
        conditions = [
            self.engine_condition,
            self.transmission_condition,
            self.suspension_condition,
            self.tyre_condition,
            self.brake_condition,
            self.electrical_condition,
            self.frame_condition,
            self.paint_condition
        ]
        # Compute average and determine pass/fail
        self.overall_rating = round(sum(conditions) / len(conditions))
        self.passed = all(c >= self.Condition.BELOW_AVERAGE for c in conditions)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inspection Report - {self.sell_request.vehicle.registration_number}"

class PurchaseOffer(BaseModel):
    """
    Purchase offer for a vehicle
    Includes pricing details and negotiation status
    """
    sell_request = models.OneToOneField(
        SellRequest,
        on_delete=models.CASCADE,
        related_name='offer',
        help_text="Related sell request"
    )

    market_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Estimated market value"
    )
    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Our offer price"
    )
    price_breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text='Format: {"base_price": 1000, "deductions": {"tyres": -100}}'
    )

    is_negotiable = models.BooleanField(
        default=True,
        help_text="Whether price is negotiable"
    )
    accepted = models.BooleanField(
        default=False,
        help_text="Whether offer was accepted"
    )
    counter_offer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Counter offer from seller"
    )
    valid_until = models.DateTimeField(
        default=get_default_valid_until,
        help_text="Offer validity period"
    )

    def save(self, *args, **kwargs):
        """Ensure a default validity period if not specified"""
        if not self.valid_until:
            self.valid_until = get_default_valid_until()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Offer for {self.sell_request.vehicle.registration_number if self.sell_request.vehicle else 'Unassigned Vehicle'}"

class VehiclePurchase(models.Model):
    """Model to handle direct vehicle purchases"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Payment Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    vehicle = models.ForeignKey('Vehicle', on_delete=models.PROTECT, related_name='purchases')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='vehicle_purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    delivery_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Purchase of {self.vehicle} by {self.buyer}"

    def complete_purchase(self):
        """Complete the purchase and transfer ownership"""
        if self.status == self.Status.PENDING:
            self.status = self.Status.COMPLETED
            self.completion_date = timezone.now()
            self.vehicle.owner = self.buyer
            self.vehicle.status = 'sold'
            self.vehicle.save()
            self.save()
            return True
        return False