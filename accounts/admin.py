from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.html import format_html
from .models import Account,Room, Facility,Booking



class AccountCreationForm(forms.ModelForm):
    """Form for creating new users in the admin with password confirmation."""
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don’t match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AccountChangeForm(forms.ModelForm):
    """Form for updating existing users in the admin, showing a read-only hash."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password',
            'is_active', 'is_staff', 'is_admin', 'is_superuser',
            'groups', 'user_permissions'
        )

    def clean_password(self):
        return self.initial["password"]



@admin.register(Account)
class AccountAdmin(UnfoldModelAdmin, UserAdmin):
    form = AccountChangeForm
    add_form = AccountCreationForm

    list_display = (
        'username', 'email', 'full_name',
        'is_staff', 'is_admin', 'is_active', 'date_joined'
    )
    list_filter = (
        'is_staff', 'is_admin', 'is_active'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    # Used by UserAdmin for "Add User" form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
    )

    # Change‐view fieldsets, collapsible by django-unfold
    fieldsets = (
        ('Login & Identity', {
            'fields': ('username', 'email', 'password'),
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name',
            ),
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_admin',
                'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    # Helper columns
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'

   

@admin.register(Facility)
class FacilityAdmin(UnfoldModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Room)
class RoomAdmin(UnfoldModelAdmin):
    list_display = ['get_name_display', 'price_per_night', 'room_image', 'size', 'bed_type', 'occupancy']
    search_fields = ['name']
    list_filter = ['name', 'facilities']
    filter_horizontal = ['facilities']

    readonly_fields = ['room_image']

    def room_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" height="80" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No image"

    room_image.short_description = "Image"
    
    
    
    
@admin.register(Booking)
class BookingAdmin(UnfoldModelAdmin):
    list_display = (
        'full_name',
        'room_type',
        'guests',
        'nights',
        'price_per_night',
        'total_price',
        'country',
        'agreed_to_terms',
        'date_created',
    )
    list_filter = ('room_type', 'country', 'agreed_to_terms', 'date_created')
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone',
        'address',
        'city',
        'state',
        'room_type',
    )
    ordering = ('-date_created',)
    readonly_fields = ('total_price', 'date_created')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Customer"    