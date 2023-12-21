from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from allauth.account.forms import LoginForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import UserProfile, Company


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["login"].label = "E-Mail Address"
        self.fields["password"].label = "Password"
        self.helper.layout = Layout(
            Fieldset(
                "",
                HTML("""<h1 class="h3 mb-3 fw-normal">Login</h1>"""),
                FloatingField("login"),
                FloatingField("password"),
                "remember",
            ),
            Submit("submit", "Sign In", css_class="w-100"),
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "phone_number")


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("company_name", "zip_code", "address_lines", "city", "state")

    def clean_company_name(self):
        company_name = self.cleaned_data["company_name"]
        if not company_name:
            raise ValidationError("Please fill out the Company Name!")

        return company_name

    def clean_zip_code(self):
        zip_code = self.cleaned_data["zip_code"]
        if not zip_code:
            raise ValidationError("Please fill out the Zip Code!")

        if ' ' in zip_code:
            raise ValidationError("Please remove spaces from the Zip Code!")

        if not zip_code.isdigit():  # Checks if all characters are digits
            raise ValidationError("Please use numbers in the Zip Code!")

        if len(zip_code) != 5:
            raise ValidationError("Please enter a 5-digit US Zip Code!")

        return zip_code


# These are for Django Admin only
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
        )
