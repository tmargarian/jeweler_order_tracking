from django.contrib import admin
from .models import Order, Client, Note

admin.site.register(Order)
admin.site.register(Client)
admin.site.register(Note)
