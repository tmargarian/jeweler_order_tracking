from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class CustomUser(AbstractUser):
    is_owner = models.BooleanField(default=True)
    is_employee = models.BooleanField(default=False)
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="users", blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        from order_tracking.models import Client, Order, Note
        self.is_active = False
        Company.objects.filter(users=self).update(deleted_flag=True)
        Owner.objects.filter(user=self).update(deleted_flag=True)
        Client.objects.filter(user=self).update(deleted_flag=True)
        Order.objects.filter(user=self).update(deleted_flag=True)
        Note.objects.filter(user=self).update(deleted_flag=True)
        self.save()


class Company(models.Model):
    company_name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="companies", blank=True)
    address_lines = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.IntegerField()
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    def delete(self, using=None, keep_parents=False):
        from order_tracking.models import Client, Order, Note
        CustomUser.objects.filter(company=self).update(deleted_flag=True)
        Owner.objects.filter(company=self).update(deleted_flag=True)
        Client.objects.filter(company=self).update(deleted_flag=True)
        Order.objects.filter(company=self).update(deleted_flag=True)
        Note.objects.filter(company=self).update(deleted_flag=True)
        self.deleted_flag = True
        self.save()


class Owner(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="owners")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owners")
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        from order_tracking.models import Client, Order
        self.deleted_flag = True
        Employee.objects.filter(user=self).update(deleted_flag=True)
        Client.objects.filter(user=self).update(deleted_flag=True)
        Order.objects.filter(user=self).update(deleted_flag=True)
        self.save()


class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employees")
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        from order_tracking.models import Client, Order
        self.user.is_active = False
        self.deleted_flag = True
        Order.objects.filter(user=self).update(deleted_flag=True)
        Client.objects.filter(user=self).update(deleted_flag=True)
        self.save()
