from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
import datetime

class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    official_email = models.EmailField(max_length=100, null=True, blank=True)
    official_address = models.TextField(null=True, blank=True)
    tax_gst_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

class SBU(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sbu_units', null=True, blank=True)
    users = models.ManyToManyField('CustomUser', related_name='sbu_users', blank=True)

    def __str__(self):
        return str(self.name)

class CustomUser(AbstractUser):
    profile_pic = models.ImageField(upload_to='assets/img/avatars', null=True, blank=True, max_length=255, help_text="Max size: 320 x 320 px, Max file size: 750KB")
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    sbu_units = models.ForeignKey(SBU, on_delete=models.SET_NULL, null=True, blank=True, related_name='sbu_units')
    is_owner = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_team_leader = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_team_leaders')
    team_leader = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_team_members')
    joining_date = models.DateField(null=True, blank=True, help_text="Date format: YYYY-MM-DD")

    def __str__(self):
        return self.username

    def get_user_role(self):
        roles = []
        if self.is_owner:
            roles.append("Owner")
        if self.is_hr:
            roles.append("HR")
        if self.is_manager:
            roles.append("Manager")
        if self.is_team_leader:
            roles.append("Team Leader")
        if self.is_employee:
            roles.append("Employee")

        return ', '.join(roles)

class BusinessCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    logo = models.ImageField(upload_to='client_logos/')
    business_name = models.CharField(max_length=255)
    business_category = models.ForeignKey(BusinessCategory, on_delete=models.SET_NULL, null=True, blank=True)
    business_details = models.TextField()
    contact_person_name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=15)
    email_address = models.EmailField()

    def __str__(self):
        return self.business_name

class ContactPage(models.Model):
    business_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    sales_number = models.CharField(max_length=15)
    support_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15)
    contact_email_address = models.EmailField()
    sales_email_address = models.EmailField()
    support_email_address = models.EmailField()
    location_map = models.TextField()  # HTML code to store embed code
    contact_image = models.ImageField(upload_to='contact_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    vision = models.TextField()
    mission = models.TextField()
    clients = models.ManyToManyField(Client)

    def __str__(self):
        return self.title

class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    paper_code = models.CharField(max_length=100)
    publish_date = models.DateField()
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # Automatically set the day of the week based on the publish_date
        if self.publish_date:
            self.day_of_week = self.publish_date.strftime('%A')  # e.g., 'Monday'
        super(Schedule, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.paper_code} - {self.publish_date} - {self.day_of_week}"