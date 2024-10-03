from django.db import models
from owner.models import Zone

# Model for ad type
class AdType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Model for ad size
class AdSize(models.Model):
    height = models.DecimalField(max_digits=5, decimal_places=2)
    width = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.height} x {self.width} cm"


# Main Ad model
class Ad(models.Model):
    SIZE_TYPE_CHOICES = [
        ('H', 'Horizontal'),
        ('V', 'Vertical'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    ad_type = models.ForeignKey(AdType, on_delete=models.SET_NULL, null=True, blank=True)  # Dropdown for Ad Type
    size = models.ForeignKey(AdSize, on_delete=models.SET_NULL, null=True, blank=True)  # Dropdown for Size
    size_type = models.CharField(max_length=1, choices=SIZE_TYPE_CHOICES, default='H')  # Horizontal/Vertical option
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    # New method to handle missing images
    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/media/ads/default_ad_image.png'  # Path to your default image


class Booking(models.Model):
    user_name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=200, blank=True)
    contact_number = models.CharField(max_length=15)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)  # The ad they are booking
    booking_description = models.TextField(blank=True)
    attachment = models.FileField(upload_to='bookings/', blank=True, null=True)  # Allows PNG, JPG, JPEG, PDF
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='Pending')  # Payment status (Pending, Completed, Failed)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user_name} for {self.ad.title}"

