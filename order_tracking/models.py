import os
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.db import models
from accounts.models import Company
from djmoney.models.fields import MoneyField


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ("purchase", "Purchase"),
        ("repair", "Repair"),
        ("other", "Other"),
    ]

    ORDER_STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="orders"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    client = models.ForeignKey(
        "Client", on_delete=models.CASCADE, related_name="orders", blank=True, null=True
    )
    order_date = models.DateField(default=timezone.now)
    order_due_date = models.DateField(default=timezone.now)
    estimated_cost = MoneyField(decimal_places=2, max_digits=10, default_currency="USD")
    quoted_price = MoneyField(decimal_places=2, max_digits=10, default_currency="USD")
    security_deposit = MoneyField(
        decimal_places=2, max_digits=10, default_currency="USD"
    )
    order_type = models.CharField(choices=ORDER_TYPE_CHOICES, default="purchase")
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, default="in_progress")
    order_photo = models.ImageField(upload_to="order_photos/", blank=True, null=True)
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # function to upload and compress image
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the model instance and the file initially

        if self.order_photo:  # Check if an image has been uploaded
            img = Image.open(self.order_photo)
            target_size = 300 * 1024  # Target size in bytes

            # Compression logic (simplified for demonstration)
            quality = 90  # Starting quality
            img_io = BytesIO()
            while img_io.tell() < target_size and quality > 0:
                img_io = BytesIO()  # Reset buffer
                img.save(img_io, format="JPEG", quality=quality)
                quality -= 10  # Decrease quality for the next iteration if needed

            # Save the compressed image back to the FileField
            self.order_photo.save(
                self.order_photo.name, ContentFile(img_io.getvalue()), save=False
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return str(
            "Order by"
            + " "
            + self.company.company_name
            + " "
            + " for "
            + self.client.first_name
            + " "
            + self.client.last_name
            if self.client
            else str(self.id)
        )

    def delete(self, using=None, keep_parents=False):
        # Soft delete associated notes
        Note.objects.filter(order=self).update(deleted_flag=True)

        # Soft delete the order
        self.deleted_flag = True
        self.save()


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_already_exists = models.BooleanField()
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="clients"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients"
    )
    first_name = models.CharField()
    last_name = models.CharField()
    phone_number = models.CharField()
    email = models.EmailField()
    total_spent = MoneyField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
        default_currency="USD",
    )
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            self.first_name + " " + self.last_name
            if self.first_name and self.last_name
            else str(self.id)
        )

    def delete(self, using=None, keep_parents=False):
        self.deleted_flag = True
        Order.objects.filter(company=self.company).update(deleted_flag=True)
        Note.objects.filter(user=self.user).update(deleted_flag=True)
        self.save()


class Note(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    deleted_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(
            "Note by" + " " + self.user.email + " for Order #" + str(self.order.id)
        )
