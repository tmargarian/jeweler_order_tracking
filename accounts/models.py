from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from localflavor.us.models import USZipCodeField, USStateField
from phonenumber_field.modelfields import PhoneNumberField


# Crucial data will be stored in CustomUser; this is what's necessary to finish Signup
class CustomUser(AbstractUser):
    # Email is the only field that CANNOT be empty to complete signup
    email = models.EmailField(max_length=100, blank=False, null=False)
    # The rest of the fields can be filled out after signup
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="users", blank=True, null=True)
    is_owner = models.BooleanField(default=True)
    is_employee = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Keeping these columns in the UserProfile
    first_name = None
    last_name = None
    phone_number = None


# Secondary data stored in the UserProfile (phone numbers | full name)
class UserProfile(models.Model):
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE, related_name="profiles")
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class Company(models.Model):
    owner = models.OneToOneField("Owner", on_delete=models.SET_NULL, related_name="owners", null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    address_lines = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zip_code = USZipCodeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name if self.company_name else str(self.id)

    class Meta:
        verbose_name_plural = "companies"


class Owner(models.Model):
    # An owner is tied to a single company and user.
    # A company can't have >1 owner
    # A user can't be related 2 owners
    company = models.OneToOneField("Company", on_delete=models.CASCADE, null=True, related_name="owners")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owners")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    # One User can only be one Employee and vice versa.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employees")
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ZipToAddressLookup(models.Model):
    zip = models.CharField(max_length=5, unique=True, primary_key=True)
    city = models.CharField(max_length=40)
    state_short = models.CharField(max_length=2)
    state_long = models.CharField(max_length=40)
    county = models.CharField(max_length=40, null=True)
    country = models.CharField(max_length=60, null=True)
    timezone = models.CharField(max_length=40, null=True)
