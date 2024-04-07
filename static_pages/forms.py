from django import forms
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Row, Column, Submit
from crispy_forms.bootstrap import PrependedAppendedText


class SupportForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        max_length=50,
        required=True,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=50,
        required=True,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = PhoneNumberField(
        label="Phone Number",
        region="US",
        required=True,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        required=True,
        initial=None,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@company.com"}
        ),
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 2}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "g-3"
        self.helper.layout = Layout(
            HTML("""<h1 class="display-6">Contact Us</h1>"""),
            Column(
                Column("first_name", css_class="col-lg-10"),
                Column("last_name", css_class="col-lg-10"),
                Column("phone_number", css_class="col-lg-10"),
                Column("email", css_class="col-lg-10"),
                Column("message", css_class="col-lg-10"),
            ),
            Submit("submit", value="Submit", css_class="btn btn-primary col-lg-6"),
        )
