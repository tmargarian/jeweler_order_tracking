from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
from django.utils import timezone
from django.db import models
from accounts.models import Company


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateField(default=timezone.now)
    order_due_date = models.DateField(default=timezone.now)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_type = models.CharField(choices=[
        ('1', 'Purchase'),
        ('2', 'Repair'),
        ('3', 'Other')],
        max_length=100)
    order_status = models.CharField(choices=[
        ('1', 'In Progress'),
        ('2', 'Complete'),
        ('3', 'Canceled')],
        max_length=100,
        default='1')
    order_photo = models.ImageField(upload_to="order_photos/", blank=True, null=True)
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        Note.objects.filter(user=self).update(deleted_flag=True)
        self.deleted_flag = True
        self.save()


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="clients")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="clients")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted_flag = True
        Order.objects.filter(user=self).update(deleted_flag=True)
        Note.objects.filter(user=self).update(deleted_flag=True)
        self.save()


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="notes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted_flag = True
        self.save()
