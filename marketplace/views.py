from decimal import Decimal
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from authback.permissions import IsOwnerOrStaff, IsStaffOrReadOnly
from .models import Vehicle, SellRequest, InspectionReport, PurchaseOffer, VehiclePurchase
from .serializers import (
    VehicleSerializer, SellRequestSerializer, 
    InspectionReportSerializer, PurchaseOfferSerializer,
    VehiclePurchaseSerializer
)
from rest_framework.exceptions import PermissionDenied

class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle model with advanced filtering and search capabilities
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filterable fields
    filterset_fields = {
        'vehicle_type': ['exact'],
        'brand': ['exact', 'in'],
        'model': ['exact', 'in'],
        'year': ['exact', 'gte', 'lte'],
        'fuel_type': ['exact'],
        'status': ['exact', 'in'],
        'price': ['gte', 'lte'],
        'emi_available': ['exact'],
    }
    
    # Searchable fields
    search_fields = ['brand', 'model', 'registration_number', 'features', 'highlights']
    
    # Orderable fields
    ordering_fields = ['price', 'year', 'kms_driven', 'created_at']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        """
        Enhance queryset with additional filtering options
        """
        queryset = super().get_queryset()
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        
        # Kilometer range filter
        min_kms = self.request.query_params.get('min_kms')
        max_kms = self.request.query_params.get('max_kms')
        if min_kms:
            queryset = queryset.filter(kms_driven__gte=int(min_kms))
        if max_kms:
            queryset = queryset.filter(kms_driven__lte=int(max_kms))
        
        # Feature filter
        features = self.request.query_params.getlist('features')
        if features:
            for feature in features:
                queryset = queryset.filter(features__contains=[feature])
        
        return queryset

    @action(detail=False, methods=['get'])
    def filters(self):
        """
        Return available filter options for the frontend
        """
        vehicles = self.get_queryset()
        return Response({
            'brands': vehicles.values_list('brand', flat=True).distinct(),
            'models': vehicles.values_list('model', flat=True).distinct(),
            'vehicle_types': dict(Vehicle.VehicleType.choices),
            'fuel_types': dict(Vehicle.FuelType.choices),
            'year_range': {
                'min': vehicles.order_by('year').values_list('year', flat=True).first(),
                'max': vehicles.order_by('-year').values_list('year', flat=True).first(),
            },
            'price_range': {
                'min': vehicles.order_by('price').values_list('price', flat=True).first(),
                'max': vehicles.order_by('-price').values_list('price', flat=True).first(),
            },
            'kms_range': {
                'min': vehicles.order_by('kms_driven').values_list('kms_driven', flat=True).first(),
                'max': vehicles.order_by('-kms_driven').values_list('kms_driven', flat=True).first(),
            }
        })

    @action(detail=False, methods=['get'])
    def featured(self):
        """
        Return featured vehicles (e.g., best deals, newly added)
        """
        # Get available vehicles with complete information
        available = self.get_queryset().filter(
            status=Vehicle.Status.AVAILABLE,
            images__has_key='thumbnail'
        ).exclude(price=0)

        # Get best deals (lowest price for their category)
        best_deals = available.order_by('vehicle_type', 'price').distinct('vehicle_type')[:5]
        
        # Get newly added vehicles
        new_arrivals = available.order_by('-created_at')[:5]
        
        return Response({
            'best_deals': VehicleSerializer(best_deals, many=True).data,
            'new_arrivals': VehicleSerializer(new_arrivals, many=True).data
        })

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Return similar vehicles based on type, price range, and brand
        """
        vehicle = self.get_object()
        price_range = (vehicle.price * Decimal('0.8'), vehicle.price * Decimal('1.2'))
        
        similar = self.get_queryset().filter(
            Q(vehicle_type=vehicle.vehicle_type) |
            Q(brand=vehicle.brand),
            price__range=price_range,
            status=Vehicle.Status.AVAILABLE
        ).exclude(id=vehicle.id)[:5]
        
        return Response(VehicleSerializer(similar, many=True).data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """Initiate purchase of a vehicle"""
        vehicle = self.get_object()
        
        if vehicle.status != 'available':
            return Response(
                {"detail": "This vehicle is not available for purchase"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VehiclePurchaseSerializer(
            data={
                'vehicle': vehicle.id,
                'amount': vehicle.price,
                'delivery_address': request.data.get('delivery_address'),
                'contact_number': request.data.get('contact_number'),
                'payment_method': request.data.get('payment_method'),
                'notes': request.data.get('notes', '')
            },
            context={'request': request}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                purchase = serializer.save()
                vehicle.status = 'pending_sale'
                vehicle.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SellRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vehicle sell requests
    """
    serializer_class = SellRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'vehicle__brand', 'vehicle__model']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        """
        Return sell requests based on user role
        """
        if self.request.user.is_staff:
            return SellRequest.objects.all()
        return SellRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new sell request and associate it with the current user
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_for_inspection(self, request, pk=None):
        """
        Submit the sell request for vehicle inspection
        """
        sell_request = self.get_object()
        
        if sell_request.status != SellRequest.Status.DRAFT:
            return Response(
                {'error': 'Only draft sell requests can be submitted for inspection'},
                status=400
            )
        
        if not sell_request.is_document_complete():
            return Response(
                {'error': 'Please complete all required documents before submission'},
                status=400
            )
        
        sell_request.status = SellRequest.Status.PENDING_INSPECTION
        sell_request.save()
        
        # Create an inspection report
        InspectionReport.objects.create(
            sell_request=sell_request,
            status=InspectionReport.Status.SCHEDULED
        )
        
        return Response({'status': 'Submitted for inspection'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a sell request
        """
        sell_request = self.get_object()
        
        if sell_request.status in [
            SellRequest.Status.COMPLETED,
            SellRequest.Status.CANCELLED
        ]:
            return Response(
                {'error': 'Cannot cancel a completed or already cancelled request'},
                status=400
            )
        
        sell_request.status = SellRequest.Status.CANCELLED
        sell_request.save()
        
        return Response({'status': 'Sell request cancelled'})

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get the timeline of events for a sell request
        """
        sell_request = self.get_object()
        
        timeline = []
        
        # Add creation event
        timeline.append({
            'date': sell_request.created_at,
            'event': 'Sell request created',
            'status': 'completed'
        })
        
        # Add document submission events
        if sell_request.registration_document:
            timeline.append({
                'date': sell_request.registration_document_uploaded_at,
                'event': 'Registration document uploaded',
                'status': 'completed'
            })
        
        if sell_request.insurance_document:
            timeline.append({
                'date': sell_request.insurance_document_uploaded_at,
                'event': 'Insurance document uploaded',
                'status': 'completed'
            })
        
        # Add inspection events
        inspection = sell_request.inspection_report.first()
        if inspection:
            timeline.append({
                'date': inspection.created_at,
                'event': 'Inspection scheduled',
                'status': 'completed' if inspection.completed_at else 'pending'
            })
            
            if inspection.completed_at:
                timeline.append({
                    'date': inspection.completed_at,
                    'event': 'Inspection completed',
                    'status': 'completed'
                })
        
        # Add completion/cancellation event
        if sell_request.status in [SellRequest.Status.COMPLETED, SellRequest.Status.CANCELLED]:
            timeline.append({
                'date': sell_request.updated_at,
                'event': f'Sell request {sell_request.status.lower()}',
                'status': 'completed'
            })
        
        return Response(sorted(timeline, key=lambda x: x['date']))

class InspectionReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vehicle inspection reports.
    
    Only staff can create/update reports, while owners can view their reports.
    """
    queryset = InspectionReport.objects.all()
    serializer_class = InspectionReportSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        'passed',
        'sell_request__vehicle__vehicle_type',
        'sell_request__status'
    ]
    ordering_fields = ['created_at', 'estimated_repair_cost', 'overall_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Staff can see all reports, users can only see their own
        """
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(sell_request__user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new inspection report and associate it with the current staff user
        """
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can create inspection reports")
        serializer.save(inspector=self.request.user)

class PurchaseOfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase offers.
    
    Includes functionality for making offers, counter-offers, and accepting/rejecting offers.
    """
    queryset = PurchaseOffer.objects.all()
    serializer_class = PurchaseOfferSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['accepted', 'is_negotiable', 'sell_request__status']
    ordering_fields = ['created_at', 'offer_price', 'valid_until']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(sell_request__user=user) | 
            Q(created_by=user)
        )

    def perform_create(self, serializer):
        """
        Create a new purchase offer and associate it with the current user
        """
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can create purchase offers")
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def counter_offer(self, request, pk=None):
        """Make a counter offer to an existing purchase offer"""
        offer = self.get_object()
        
        if not offer.is_negotiable:
            return Response(
                {"error": "This offer is not negotiable"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if offer.valid_until and offer.valid_until < timezone.now():
            return Response(
                {"error": "Offer has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        counter_price = request.data.get('counter_offer')
        if not counter_price:
            return Response(
                {"error": "counter_offer price is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        offer.counter_offer = counter_price
        offer.save()
        
        return Response(PurchaseOfferSerializer(offer).data)

class VehiclePurchaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vehicle purchases.
    
    Includes functionality for initiating purchases, processing payments,
    and completing vehicle transfers.
    """
    queryset = VehiclePurchase.objects.all()
    serializer_class = VehiclePurchaseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['purchase_date', 'completion_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(buyer=user)

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process payment for a vehicle purchase"""
        purchase = self.get_object()
        
        if purchase.status != VehiclePurchase.Status.PENDING:
            return Response(
                {"detail": "This purchase is not in pending status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Here you would integrate with your payment gateway
        # For now, we'll simulate a successful payment
        payment_successful = True
        payment_id = "SIMULATED_PAYMENT_123"

        if payment_successful:
            purchase.payment_id = payment_id
            purchase.status = VehiclePurchase.Status.PROCESSING
            purchase.save()
            return Response({"detail": "Payment processed successfully"})
        
        return Response(
            {"detail": "Payment processing failed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def complete_transfer(self, request, pk=None):
        """Complete the vehicle transfer after successful payment"""
        purchase = self.get_object()
        
        if purchase.status != VehiclePurchase.Status.PROCESSING:
            return Response(
                {"detail": "This purchase is not ready for transfer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if purchase.complete_purchase():
            return Response({"detail": "Vehicle transfer completed successfully"})
        
        return Response(
            {"detail": "Failed to complete vehicle transfer"},
            status=status.HTTP_400_BAD_REQUEST
        )