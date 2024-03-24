from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from localflavor.us.forms import USZipCodeField
from phonenumber_field.formfields import PhoneNumberField
from allauth.account.forms import LoginForm, SignupForm
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
                HTML(
                    """<h1 class="h1 mb-3 fw-normal">
                        Login
                        </h1>"""
                ),
                FloatingField("login"),
                FloatingField("password"),
                "remember",
            ),
            Submit("submit", "Log In", css_class="w-100"),
        )


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["email"].label = "E-Mail Address"
        self.fields["password1"].label = "Password"
        self.fields["password1"].help_text = None
        self.helper.layout = Layout(
            Fieldset(
                "",
                HTML(
                    """<h1 class="h1 mb-3 fw-normal">
                        Sign Up
                    </h1>"""
                ),
                FloatingField("email"),
                FloatingField("password1"),
            ),
            Submit("submit", "Sign Up", css_class="w-100"),
        )


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["first_name"].label = "First Name"
        self.fields["last_name"].label = "Last Name"
        self.fields["phone_number"].label = "Phone Number"

    # TODO: Check if this is requried considering the model already has PhoneNumberField
    phone_number = PhoneNumberField(region="US", required=False)

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "phone_number")

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        if not first_name:
            raise ValidationError("Please fill out the First Name!")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        if not last_name:
            raise ValidationError("Please fill out the Last Name!")

        return last_name


class CompanyForm(forms.ModelForm):

    # Overriding the default error message (it features 5 AND 9 digit zips like 94089-1690)
    zip_code = USZipCodeField(
        error_messages={"invalid": "Enter a zip code in the format XXXXX."},
        required=False,
    )

    class Meta:
        model = Company
        fields = ("company_name", "zip_code", "address_lines", "city", "state")

    def clean_company_name(self):
        company_name = self.cleaned_data["company_name"]
        if not company_name:
            raise ValidationError("Please fill out the Company Name!")

        return company_name

    def clean_zip_code(self):
        # Most of the cleaning if performed by localflavor package
        zip_code = self.cleaned_data["zip_code"]
        if not zip_code:
            raise ValidationError("Please fill out the Zip Code!")

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
