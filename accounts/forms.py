from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from allauth.account.forms import LoginForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_bootstrap5.bootstrap5 import FloatingField


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['login'].label = "E-Mail Address"
        self.fields['password'].label = "Password"
        self.helper.layout = Layout(
            Fieldset(
                "",
                HTML("""<h1 class="h3 mb-3 fw-normal">Login</h1>"""),
                FloatingField("login"),
                FloatingField("password"),
                "remember"
            ),
            Submit("submit", "Sign In", css_class="w-100"),
        )


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
