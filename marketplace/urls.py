from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellRequestViewSet, InspectionReportViewSet, PurchaseOfferViewSet

router = DefaultRouter()
router.register('sell-requests', SellRequestViewSet, basename='sellrequest')
router.register('inspections', InspectionReportViewSet, basename='inspection')
router.register('offers', PurchaseOfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)),
]