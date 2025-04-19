# from django.urls import path
# from repairing_service.views import (
#     ManufacturerListView, VehicleModelListView, ServiceCategoryListView, 
#     ServiceListByCategoryView, ServicePriceDetailView, AddToCartView, 
#     CartDetailView, RemoveCartItemView
#     # , AddReviewView, ServiceReviewsView, 
#     # AddCommentView
# )

# urlpatterns = [
#     # 🚗 Manufacturer & Vehicle Model Endpoints
#     path('manufacturers/', ManufacturerListView.as_view(), name='manufacturer-list'),
#     path('manufacturers/<int:manufacturer_id>/models/', VehicleModelListView.as_view(), name='vehicle-models'),
#     # 🔧 Service Categories & Services
#     path('categories/', ServiceCategoryListView.as_view(), name='category-list'),
#     path('categories/<uuid:category_id>/services/', ServiceListByCategoryView.as_view(), name='service-list'),

#     # 💰 Service Pricing
#     path(
#         'services/<uuid:service_id>/manufacturers/<int:manufacturer_id>/models/<int:vehicle_model_id>/price/', 
#         ServicePriceDetailView.as_view(), name='service-price-detail'
#     ),
#     path(
#         'services/<uuid:service_id>/manufacturers/<int:manufacturer_id>/models/<int:vehicle_model_id>/price/', 
#         ServicePriceDetailView.as_view(), name='service-price-detail'
#     ),

#     # 🛒 Cart Operations
#     path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
#     path('cart/', CartDetailView.as_view(), name='cart-detail'),
#     path('cart/item/<uuid:cart_item_id>/remove/', RemoveCartItemView.as_view(), name='remove-cart-item'),

#     # ⭐ Reviews & Comments
#     # path('service/<uuid:service_id>/reviews/', ServiceReviewsView.as_view(), name='service-reviews'),
#     # path('reviews/<uuid:review_id>/comment/', AddCommentView.as_view(), name='add-comment'),
#     # path('reviews/add/', AddReviewView.as_view(), name='add-review'),
# ]




from django.urls import path
from repairing_service.views import (
    ManufacturerListView,
    VehicleModelListView,
    ServiceCategoryListView,
    ServiceListByCategoryView,
    ServicePriceDetailView,
    AddToCartView,
    CartDetailView,
    RemoveCartItemView
)

urlpatterns = [
    # Manufacturer & Vehicle Model Endpoints
    path('manufacturers/', ManufacturerListView.as_view(), name='manufacturer-list'),
    path('manufacturers/<int:manufacturer_id>/models/', VehicleModelListView.as_view(), name='vehicle-models'),
    # Service Categories & Services
    path('categories/', ServiceCategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:category_id>/services/', ServiceListByCategoryView.as_view(), name='service-list'),

    # Service Pricing
    # path('services/<uuid:service_id>/manufacturers/<uuid:manufacturer_id>/models/<uuid:vehicle_model_id>/price/', ServicePriceDetailView.as_view(), name='service-price-detail'),
    path('services/<uuid:service_id>/manufacturers/<int:manufacturer_id>/models/<int:vehicle_model_id>/price/', ServicePriceDetailView.as_view(), name='service-price-detail'),

    # Cart Operations
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    # path('cart/add/<int:service_id>/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/item/<uuid:cart_item_id>/remove/', RemoveCartItemView.as_view(), name='remove-cart-item'),
]

# path('services/<uuid:service_id>/manufacturers/<int:manufacturer_id>/models/<int:vehicle_model_id>/price/', ServicePriceDetailView.as_view(), name='service-price-detail'),
