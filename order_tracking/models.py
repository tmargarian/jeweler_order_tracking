import uuid
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.db import models
from accounts.models import Company
from phonenumber_field.modelfields import PhoneNumberField


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
    order_date = models.DateField(default=False)
    order_due_date = models.DateField(default=False)
    estimated_cost = models.DecimalField(decimal_places=2, max_digits=10)
    quoted_price = models.DecimalField(decimal_places=2, max_digits=10)
    security_deposit = models.DecimalField(default=0, decimal_places=2, max_digits=10)
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
            img = Image.open(self.order_photo.path)
            target_size = 300 * 1024  # Target size in bytes 300 KB

            format = img.format # Get the image format (e.g., JPEG, PNG)

            img_io = BytesIO()  # Create a BytesIO buffer for image compression

            # Define initial and final quality settings
            initial_quality = 91  # Set it to a high value to allow more aggressive quality reduction
            final_quality = 10

            while True:
                img_io.truncate(0)  # Clear the buffer
                img_io.seek(0)  # Reset the position to write new data from the beginning

                # Attempt to compress the image with the current quality
                img.save(img_io, format=format, quality=initial_quality)

                # Check the size of the compressed image
                current_size = img_io.tell()

                if current_size <= target_size or initial_quality <= final_quality:
                    # If the size is below the target or the quality can't be reduced further, exit the loop
                    break

                # Reduce the image quality
                initial_quality -= 10  # Reduce by 1 (fine-grained control)

            # Save the compressed image to a temporary location
            temp_path = self.order_photo.path + '_temp'
            with open(temp_path, 'wb') as f:
                f.write(img_io.getvalue())

            # Replace the original image with the compressed image
            os.remove(self.order_photo.path)
            os.rename(temp_path, self.order_photo.path)

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
    phone_number = PhoneNumberField(blank=True, null=True, region="US")
    email = models.EmailField()
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
