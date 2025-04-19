# from uuid import UUID
# from rest_framework import viewsets, generics, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.decorators import action
# from django.shortcuts import get_object_or_404
# from rest_framework.exceptions import ValidationError
# from .models import (
#     VehicleModel, ServiceCategory, Feature, Service, ServicePrice, 
#     Cart, CartItem
# )
# from .serializers import (
#     VehicleModelSerializer, ServiceCategorySerializer, FeatureSerializer, 
#     ServiceSerializer, ServicePriceSerializer, CartSerializer, CartItemSerializer, 
# )
# from vehicle.serializers import ManufacturerSerializer
# from vehicle.models import Manufacturer

# # 🚗 List all Manufacturers
# class ManufacturerListView(generics.ListAPIView):
#     queryset = Manufacturer.objects.all()
#     serializer_class = ManufacturerSerializer
#     permission_classes = [AllowAny]


# # # 🚗 List all Vehicle Models for a Manufacturer
# # class VehicleModelListView(generics.ListAPIView):
# #     serializer_class = VehicleModelSerializer
# #     permission_classes = [AllowAny]

# #     def get_queryset(self):
# #         try:
# #             manufacturer_uuid = UUID(self.kwargs['manufacturer_id'])  # Convert to UUID
# #         except ValueError:
# #             raise ValidationError("Invalid UUID format")
# #         return VehicleModel.objects.filter(manufacturer_id=manufacturer_uuid)



# class VehicleModelListView(generics.ListAPIView):
#     serializer_class = VehicleModelSerializer
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         try:
#             # manufacturer_uuid = str(self.kwargs['manufacturer_id'])  # Convert to UUID
#             manufacturer_uuid = UUID(self.kwargs['manufacturer_id'])  # Convert to UUID
#         except ValueError:
#             raise ValidationError("Invalid UUID format")
#         return VehicleModel.objects.filter(manufacturer_id=manufacturer_uuid)


# # 🔧 List all Service Categories
# class ServiceCategoryListView(generics.ListAPIView):
#     queryset = ServiceCategory.objects.all()
#     serializer_class = ServiceCategorySerializer
#     permission_classes = [AllowAny]


# # 🔧 List Services for a Specific Subcategory
# class ServiceListByCategoryView(generics.ListAPIView):
#     serializer_class = ServiceSerializer
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         return Service.objects.filter(category_id=self.kwargs['category_id'])


# # 💰 Get Pricing for a Service, Manufacturer, and Vehicle Model
# # class ServicePriceDetailView(generics.RetrieveAPIView):
# #     serializer_class = ServicePriceSerializer
# #     permission_classes = [AllowAny]

# #     def get_object(self):
# #         try:
# #             service_uuid = UUID(self.kwargs['service_id'])
# #             manufacturer_uuid = UUID(self.kwargs['manufacturer_id'])
# #             vehicle_model_uuid = UUID(self.kwargs['vehicle_model_id'])
# #         except ValueError:
# #             raise ValidationError("Invalid UUID format")

# #         return get_object_or_404(
# #             ServicePrice,
# #             service_id=service_uuid,
# #             manufacturer_id=manufacturer_uuid,
# #             vehicle_model_id=vehicle_model_uuid
# #         )
# class ServicePriceDetailView(generics.RetrieveAPIView):
#     serializer_class = ServicePriceSerializer
#     permission_classes = [AllowAny]

#     def get_object(self):
#         try:
#             # Convert UUID to string if required
#             service_uuid = str(UUID(self.kwargs['service_id']))  # Ensure it is a string
#             manufacturer_uuid = str(UUID(self.kwargs['manufacturer_id']))  # Convert to string
#             vehicle_model_uuid = str(UUID(self.kwargs['vehicle_model_id']))  # Convert to string
#         except ValueError:
#             raise ValidationError("Invalid UUID format")

#         return get_object_or_404(
#             ServicePrice,
#             service_id=service_uuid,  # Use string here
#             manufacturer_id=manufacturer_uuid,  # Use string here
#             vehicle_model_id=vehicle_model_uuid  # Use string here
#         )



# # 🛂 Add Service to Cart
# class AddToCartView(generics.CreateAPIView):
#     serializer_class = CartItemSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         try:
#             service_uuid = UUID(request.data.get('service_id'))
#             manufacturer_uuid = UUID(request.data.get('manufacturer_id'))
#             vehicle_model_uuid = UUID(request.data.get('vehicle_model_id'))
#         except ValueError:
#             return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

#         service = get_object_or_404(Service, id=service_uuid)
#         manufacturer = get_object_or_404(Manufacturer, id=manufacturer_uuid)
#         vehicle_model = get_object_or_404(VehicleModel, id=vehicle_model_uuid)

#         cart, _ = Cart.objects.get_or_create(user=user)
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart, service=service, manufacturer=manufacturer, vehicle_model=vehicle_model,
#             defaults={'quantity': request.data.get('quantity', 1)}
#         )

#         if not created:
#             cart_item.quantity += int(request.data.get('quantity', 1))
#             cart_item.save()

#         return Response({'message': 'Service added to cart'}, status=status.HTTP_201_CREATED)



# # 🛂 Show Cart
# class CartDetailView(generics.RetrieveAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         cart, _ = Cart.objects.get_or_create(user=self.request.user)
#         return cart


# # 🛂 Remove Item from Cart
# class RemoveCartItemView(generics.DestroyAPIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, *args, **kwargs):
#         cart_item = get_object_or_404(CartItem, id=kwargs['cart_item_id'], cart__user=request.user)
#         cart_item.delete()
#         return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)





from rest_framework.generics import CreateAPIView

from rest_framework.views import APIView
from uuid import UUID
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .models import (
    VehicleModel,
    ServiceCategory,
    Feature,
    Service,
    ServicePrice,
    Cart,
    CartItem
)
from .serializers import (
    VehicleModelSerializer,
    ServiceCategorySerializer,
    FeatureSerializer,
    ServiceSerializer,
    ServicePriceSerializer,
    CartSerializer,
    CartItemSerializer,
)
from vehicle.serializers import ManufacturerSerializer
from vehicle.models import Manufacturer

# List all Manufacturers
class ManufacturerListView(generics.ListAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [AllowAny]

# List all Vehicle Models for a Manufacturer
# class VehicleModelListView(generics.ListAPIView):
#     serializer_class = VehicleModelSerializer
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         try:
#             manufacturer_uuid = UUID(self.kwargs['manufacturer_id'])
#             manufacturer_uuid_str = manufacturer_uuid.hex
#         except ValueError:
#             raise ValidationError("Invalid UUID format")
#         return VehicleModel.objects.filter(manufacturer_id=manufacturer_uuid_str)

# class VehicleModelListView(generics.ListAPIView):
#     serializer_class = VehicleModelSerializer
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         try:
#             manufacturer_uuid = UUID(self.kwargs['manufacturer_id'])
#             manufacturer_uuid_str = manufacturer_uuid.hex
#         except ValueError:
#             raise ValidationError("Invalid UUID format")
#         return VehicleModel.objects.filter(manufacturer_id=manufacturer_uuid_str)


class VehicleModelListView(generics.ListAPIView):
    serializer_class = VehicleModelSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        manufacturer_id = self.kwargs['manufacturer_id']
        return VehicleModel.objects.filter(manufacturer_id=manufacturer_id)

# List all Service Categories
class ServiceCategoryListView(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]

# List Services for a Specific Subcategory
class ServiceListByCategoryView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Service.objects.filter(category_id=self.kwargs['category_id'])

# Get Pricing for a Service, Manufacturer, and Vehicle Model
# class ServicePriceDetailView(generics.RetrieveAPIView):
#     serializer_class = ServicePriceSerializer
#     permission_classes = [AllowAny]

#     def get_object(self):
#         try:
#             service_uuid = UUID(self.kwargs['service_id'])
#             service_uuid_str = service_uuid.hex
#             manufacturer_uuid = UUID(self.kwargs['manufacturer_id'])
#             manufacturer_uuid_str = manufacturer_uuid.hex
#             vehicle_model_uuid = UUID(self.kwargs['vehicle_model_id'])
#             vehicle_model_uuid_str = vehicle_model_uuid.hex
#         except ValueError:
#             raise ValidationError("Invalid UUID format")
#         return get_object_or_404(
#             ServicePrice,
#             service_id=service_uuid_str,
#             manufacturer_id=manufacturer_uuid_str,
#             vehicle_model_id=vehicle_model_uuid_str
#         )



class ServicePriceDetailView(generics.RetrieveAPIView):
    serializer_class = ServicePriceSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        service_uuid = self.kwargs['service_id']
        manufacturer_id = self.kwargs['manufacturer_id']
        vehicle_model_id = self.kwargs['vehicle_model_id']
        return get_object_or_404(
            ServicePrice,
            service_id=service_uuid,
            manufacturer_id=manufacturer_id,
            vehicles_model_id=vehicle_model_id
        )

# Add Service to Cart
# class AddToCartView(generics.CreateAPIView):
#     serializer_class = CartItemSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         try:
#             service_uuid = UUID(request.data.get('service_id'))
#             service_uuid_str = service_uuid.hex
#             manufacturer_uuid = UUID(request.data.get('manufacturer_id'))
#             manufacturer_uuid_str = manufacturer_uuid.hex
#             vehicle_model_uuid = UUID(request.data.get('vehicle_model_id'))
#             vehicle_model_uuid_str = vehicle_model_uuid.hex
#         except ValueError:
#             return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
#         service = get_object_or_404(Service, id=service_uuid_str)
#         manufacturer = get_object_or_404(Manufacturer, id=manufacturer_uuid_str)
#         vehicle_model = get_object_or_404(VehicleModel, id=vehicle_model_uuid_str)
#         cart, _ = Cart.objects.get_or_create(user=user)
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             service=service,
#             manufacturer=manufacturer,
#             vehicle_model=vehicle_model,
#             defaults={'quantity': request.data.get('quantity', 1)}
#         )
#         if not created:
#             cart_item.quantity += int(request.data.get('quantity', 1))
#             cart_item.save()
#         return Response({'message': 'Service added to cart'}, status=status.HTTP_201_CREATED)


# Add Service to Cart
# Add Service to Cart
# class AddToCartView(generics.CreateAPIView):
#     serializer_class = CartItemSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         service_uuid = request.data.get('service_id')
#         manufacturer_id = request.data.get('manufacturer_id')
#         vehicle_model_id = request.data.get('vehicle_model_id')

#         service = get_object_or_404(Service, uuid=service_uuid)
#         manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)
#         vehicle_model = get_object_or_404(VehicleModel, id=vehicle_model_id)

#         cart, _ = Cart.objects.get_or_create(user=user)
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart, service=service, manufacturer=manufacturer, vehicle_model=vehicle_model,
#             defaults={'quantity': request.data.get('quantity', 1)}
#         )

#         if not created:
#             cart_item.quantity += int(request.data.get('quantity', 1))
#             cart_item.save()

#         return Response({'message': 'Service added to cart'}, status=status.HTTP_201_CREATED)


# from uuid import UUID
# from django.db import transaction, IntegrityError
# from django.shortcuts import get_object_or_404
# from rest_framework import status
# from rest_framework.generics import CreateAPIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import Service, Cart, CartItem
# from .serializers import CartItemSerializer

# class AddToCartView(CreateAPIView):
#     serializer_class = CartItemSerializer
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def create(self, request, *args, **kwargs):
#         user = request.user
#         service_id = request.data.get('service_id')
#         quantity = request.data.get('quantity', 1)

#         # Validate service_id existence
#         if not service_id:
#             return Response({"error": "service_id is required"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             service_uuid = UUID(service_id)
#         except ValueError:
#             return Response({"error": "Invalid UUID format for service_id"}, status=status.HTTP_400_BAD_REQUEST)

#         # Retrieve the Service instance; returns 404 if not found
#         service = get_object_or_404(Service, uuid=service_uuid)

#         try:
#             # Get or create the user's cart
#             cart, _ = Cart.objects.get_or_create(user=user)

#             # Get or create the CartItem; unique_together ensures one entry per service in a cart
#             cart_item, created = CartItem.objects.get_or_create(
#                 cart=cart,
#                 service=service,
#                 defaults={'quantity': quantity}
#             )

#             # If the item already exists, update the quantity
#             if not created:
#                 cart_item.quantity += int(quantity)
#                 cart_item.save()

#         except IntegrityError:
#             # Rollback transaction automatically and return error response
#             return Response({"error": "Integrity error: related foreign key record might be missing."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         return Response({'message': 'Service added to cart'}, status=status.HTTP_201_CREATED)









# # Show Cart
# class CartDetailView(generics.RetrieveAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         cart, _ = Cart.objects.get_or_create(user=self.request.user)
#         return cart

# # Remove Item from Cart
# class RemoveCartItemView(generics.DestroyAPIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, *args, **kwargs):
#         cart_item = get_object_or_404(CartItem, id=kwargs['cart_item_id'], cart__user=request.user)
#         cart_item.delete()
#         return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)



from uuid import UUID
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Service, Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer

class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        service_id = request.data.get('service_id')
        quantity = request.data.get('quantity', 1)

        # Validate service_id existence
        if not service_id:
            return Response({"error": "service_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service_uuid = UUID(service_id)
        except ValueError:
            return Response({"error": "Invalid UUID format for service_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the Service instance; returns 404 if not found
        service = get_object_or_404(Service, uuid=service_uuid)

        try:
            # Ensure the user exists
            if not user.is_authenticated:
                return Response({"error": "User authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

            # Ensure the user has a cart
            cart, created = Cart.objects.get_or_create(user=user)
            if created:
                print(f"✅ Cart created for user {user.id}")

            # Ensure the service exists before adding to cart
            if not service:
                return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get or create the CartItem; unique_together ensures one entry per service in a cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                service=service,
                defaults={'quantity': quantity}
            )

            # If the item already exists, update the quantity
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()

        except IntegrityError:
            # Rollback transaction automatically and return error response
            return Response({"error": "Integrity error: related foreign key record might be missing."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Service added to cart'}, status=status.HTTP_201_CREATED)

# Show Cart
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

# Remove Item from Cart
class RemoveCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=kwargs['cart_item_id'], cart__user=request.user)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)



class CartItemCreateView(CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def create(self, request, *args, **kwargs):
        service_id = request.data.get("service")
        manufacturer_id = request.data.get("manufacturer")
        vehicle_model_id = request.data.get("vehicle_model")
        user_id = request.data.get("user")

        if not service_id or not manufacturer_id or not vehicle_model_id:
            return Response({"error": "service, manufacturer, and vehicle_model are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(uuid=service_id)
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            vehicle_model = VehicleModel.objects.get(id=vehicle_model_id)
            cart, _ = Cart.objects.get_or_create(user_id=user_id)
        except (Service.DoesNotExist, Manufacturer.DoesNotExist, VehicleModel.DoesNotExist):
            return Response({"error": "Invalid service, manufacturer, or vehicle_model"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            service=service,
            manufacturer=manufacturer,
            vehicle_model=vehicle_model,
            defaults={"quantity": request.data.get("quantity", 1)}
        )

        if not created:
            cart_item.quantity += int(request.data.get("quantity", 1))
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)