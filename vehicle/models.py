from django.db import models
from accounts.models import UserProfile

class VehicleType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='vehicle_types/', null=True, blank=True)

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='manufacturer_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class VehicleModel(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicle_models/', null=True, blank=True)

    class Meta:
        unique_together = ('name', 'manufacturer')

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"

class UserVehicle(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateField(null=True, blank=True)
    vehicle_image = models.ImageField(upload_to='user_vehicles/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s {self.model}"
