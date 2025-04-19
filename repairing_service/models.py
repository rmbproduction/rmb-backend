import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.apps import apps
from vehicle.models import Manufacturer, VehicleModel

class Feature(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='serviceCategory_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    manufacturers = models.ManyToManyField(Manufacturer, related_name='services', blank=True)
    vehicles_models = models.ManyToManyField(VehicleModel, related_name='services', blank=True)
    category = models.ForeignKey(ServiceCategory, related_name='services', on_delete=models.CASCADE, null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField()
    duration = models.CharField(max_length=255)
    warranty = models.CharField(max_length=255)
    recommended = models.CharField(max_length=20)
    features = models.ManyToManyField(Feature, related_name="services", blank=True)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discounted_price(self):
        return self.base_price - (self.base_price * (self.discount / 100))

    def get_price(self, manufacturer=None, vehicle_model=None):
        ServicePrice = apps.get_model('repairing_service', 'ServicePrice')
        if vehicle_model:
            service_price = ServicePrice.objects.filter(service=self, vehicles_model=vehicle_model).first()
            if service_price:
                return service_price.price
        if manufacturer:
            service_price = ServicePrice.objects.filter(service=self, manufacturer=manufacturer, vehicles_model__isnull=True).first()
            if service_price:
                return service_price.price
        return self.base_price

    def __str__(self):
        return self.name

class ServicePrice(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey("vehicle.Manufacturer", on_delete=models.CASCADE)
    vehicles_model = models.ForeignKey("vehicle.VehicleModel", related_name='service_prices', null=True, blank=True, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('service', 'manufacturer', 'vehicles_model')

    def __str__(self):
        return f"Price for {self.service.name}: {self.price}"



class Cart(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='carts', on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, through='CartItem')

    def __str__(self):
        return f'Cart for {self.user.email}'


class CartItem(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'service')

    def __str__(self):
        return f'{self.quantity} of {self.service.name}'



