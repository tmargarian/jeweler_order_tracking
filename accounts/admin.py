from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Company, Owner, UserProfile

from .forms import CustomUserCreationForm, CustomUserChangeForm


CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "is_superuser",
    ]

    fieldsets = (
        (None, {'fields': ('company', 'email', 'is_owner', 'is_employee')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(Owner)
admin.site.register(UserProfile)

