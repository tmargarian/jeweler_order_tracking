from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class CustomUser(AbstractUser):
    # Email is the only field that CANNOT be empty to complete signup
    email = models.EmailField(max_length=100, blank=False, null=False)
    # The rest of the fields can be filled out after signup
    is_owner = models.BooleanField(default=True)
    is_employee = models.BooleanField(default=False)
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="users", blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class Company(models.Model):
    company_name = models.CharField(max_length=100)
    address_lines = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = "companies"


class Owner(models.Model):
    # An owner is tied to a single company and user.
    # A company can't have >1 owner
    # A user can't be related 2 owners
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="owners")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owners")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    # One User can only be one Emplyee and vice versa.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employees")
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
