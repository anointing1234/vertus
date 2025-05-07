import json
import locale
import random
import string
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField




class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The username is required")
        if not email:
            raise ValueError("The email address is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The username is required for superusers")
        if not email:
            raise ValueError("The email address is required for superusers")
        if not password:
            raise ValueError("The password is required for superusers")

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email=email, username=username, password=password, **extra_fields)




class Account(AbstractBaseUser, PermissionsMixin):
    # Login & identity
    username        = models.CharField(max_length=150, unique=True)
    email           = models.EmailField(max_length=254, unique=True)
    first_name      = models.CharField(max_length=30)
    last_name       = models.CharField(max_length=30)

   
    # Meta
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now=True)

    # Permissions
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_admin        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)

    # Manager & auth setup
    objects         = AccountManager()
    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True



class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_CATEGORIES = [
        ('standard', 'Standard Room'),
        ('presidential', '1 Bedroom Presidentail'),
        ('presidential2', '2 Bedroom Presidential'),
        ('suite', '1 Bedroom Suite'),
        ('suite2', '2 Bedroom Suite'),
        ('executive', 'Executive Deluxe'),
        ('Deluxe','Deluxe Rooms')
    ]

    name = models.CharField(max_length=50, choices=ROOM_CATEGORIES, unique=True)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)

    size = models.CharField(max_length=20, default="600 Sq")
    bed_type = models.CharField(max_length=50, default="2 Single Bed")
    occupancy = models.CharField(max_length=50, default="Three Persons")

    facilities = models.ManyToManyField(Facility, blank=True)

    def __str__(self):
        return f"{self.get_name_display()} - ${self.price_per_night}/night"

    def list_facilities(self):
        return ", ".join([facility.name for facility in self.facilities.all()])

   

class Booking(models.Model):
    # Room and stay details
    room_type = models.CharField(max_length=100)  # e.g. "Deluxe Room", "Suite"
    guests = models.PositiveIntegerField()
    nights = models.PositiveIntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Billing Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = CountryField()
    check_in = models.DateField(null=True)  # Change to DateField if currently DateTimeField
    check_out = models.DateField(null=True) 

    # Extra Information
    special_requests = models.TextField(blank=True, null=True)
    agreed_to_terms = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_type} booking by {self.first_name} {self.last_name}"

    def calculate_total_price(self):
        return self.nights * self.price_per_night