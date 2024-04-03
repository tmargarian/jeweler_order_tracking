from django import forms
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Row, Column, Submit
from crispy_forms.bootstrap import PrependedAppendedText

from .models import Order, Client


class OrderCreateForm(forms.ModelForm):
    client_already_exists = forms.BooleanField(
        label="Existing Client?",
        required=False,
        initial=False,
        widget=forms.Select(
            choices=[(True, "Yes"), (False, "No")], attrs={"class": "form-control"}
        ),
    )
    first_name = forms.CharField(
        label="Client First Name",
        max_length=50,
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label="Client Last Name",
        max_length=50,
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = PhoneNumberField(
        label="Client Phone Number",
        region="US",
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Client Email Address",
        max_length=254,
        required=False,
        initial=None,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@company.com"}
        ),
    )
    client = forms.ModelChoiceField(
        label="Client",
        queryset=Client.objects.all(),
        required=False,
        initial=None,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    content = forms.CharField(
        label="Add Note", widget=forms.Textarea(attrs={"rows": 2}), required=False
    )

    class Meta:
        model = Order
        fields = (
            "client_already_exists",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "client",
            "order_type",
            "order_status",
            "order_date",
            "order_due_date",
            "estimated_cost",
            "quoted_price",
            "security_deposit",
            "order_photo",
            "content",
        )

        # This overrides widgets of ONLY the Order fields
        # For other fields (client + content) edit the definitions above
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "order_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["client"].queryset = Client.objects.filter(
                company=self.user.company, deleted_flag=False
            )

        self.helper = FormHelper()
        self.helper.form_class = "g-3"
        self.helper.layout = Layout(
            HTML("""<h1 class="display-6">Client Fields</h1>"""),
            Row(
                Column("client_already_exists", css_class="col-lg-6"),
                Column("client", css_class="col-lg-6"),
                Column("first_name", css_class="col-lg-6"),
                Column("last_name", css_class="col-lg-6"),
                Column("phone_number", css_class="col-lg-6"),
                Column("email", css_class="col-lg-6"),
            ),
            HTML("""<h1 class="display-6">Order Fields</h1>"""),
            Row(
                Column("order_type", css_class="col-lg-6"),
                Column("order_status", css_class="col-lg-6"),
                Column("order_date", css_class="col-lg-6"),
                Column("order_due_date", css_class="col-lg-6"),
                Column(
                    PrependedAppendedText("estimated_cost", "$"),
                    css_class="col-lg-4",
                ),
                Column(
                    PrependedAppendedText("quoted_price", "$"),
                    css_class="col-lg-4",
                ),
                Column(
                    PrependedAppendedText("security_deposit", "$"),
                    css_class="col-lg-4",
                ),
                Column("order_photo", css_class="col-lg-12"),
                Column("content", css_class="col-lg-12"),
            ),
            Submit("submit", value="Submit", css_class="btn btn-primary col-lg-6"),
        )

    def clean(self):
        cleaned_data = super().clean()
        client_already_exists = cleaned_data.get("client_already_exists")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        phone_number = cleaned_data.get("phone_number")
        client = cleaned_data.get("client")
        order_date = cleaned_data.get("order_date")
        order_due_date = cleaned_data.get("order_due_date")
        estimated_cost = cleaned_data.get("estimated_cost")
        quoted_price = cleaned_data.get("quoted_price")
        security_deposit = cleaned_data.get("security_deposit")
        order_photo = cleaned_data.get("order_photo")

        if not client_already_exists:
            if not first_name:
                self.add_error("first_name", "This field is required.")

            if not last_name:
                self.add_error("last_name", "This field is required.")

            if not phone_number:
                self.add_error("phone_number", "This field is required.")

        if client_already_exists:
            if not client:
                self.add_error("client", "This field is required.")

        if order_due_date < order_date:
            self.add_error("order_due_date", "Due date cannot be before order date")

        if quoted_price < estimated_cost:
            self.add_error(
                "quoted_price", "Quoted price cannot be less than estimated cost"
            )

        if security_deposit > quoted_price:
            self.add_error(
                "security_deposit",
                "Security deposit cannot be greater than quoted price",
            )

        if quoted_price < 0:
            self.add_error(
                "quoted_price", "Quoted price cannot be negative"
            )

        if estimated_cost < 0:
            self.add_error(
                "estimated_cost", "Estimated cost cannot be negative"
            )

        if security_deposit < 0:
            self.add_error(
                "security_deposit", "Security deposit cannot be negative"
            )

        if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
            self.add_error("order_photo", "File size should not exceed 6 MB.")

        return cleaned_data


class OrderUpdateForm(forms.ModelForm):
    content = forms.CharField(
        label=" ",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Add notes here"}),
        required=False
    )

    class Meta:
        model = Order
        fields = (
            "client",
            "order_type",
            "order_status",
            "order_date",
            "order_due_date",
            "estimated_cost",
            "quoted_price",
            "security_deposit",
            "order_photo",
            "content",
        )

        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "order_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["client"].queryset = Client.objects.filter(
                company=self.user.company, deleted_flag=False
            )

        self.helper = FormHelper()
        self.helper.form_class = "g-3"
        self.helper.layout = Layout(
            HTML("""<h1 class="display-6">Client Fields</h1>"""),
            Row(
                Column("client", css_class="col-lg-6"),
            ),
            HTML("""<h1 class="display-6">Order Fields</h1>"""),
            Row(
                Column("order_type", css_class="col-lg-6"),
                Column("order_status", css_class="col-lg-6"),
                Column("order_date", css_class="col-lg-6"),
                Column("order_due_date", css_class="col-lg-6"),
                Column(
                    PrependedAppendedText("estimated_cost", "$"),
                    css_class="col-lg-4",
                ),
                Column(
                    PrependedAppendedText("quoted_price", "$"),
                    css_class="col-lg-4",
                ),
                Column(
                    PrependedAppendedText("security_deposit", "$"),
                    css_class="col-lg-4",
                ),
                Column("order_photo", css_class="col-lg-8"),
            ),
            Submit("submit", value="Submit", css_class="btn btn-primary col-lg-3"),
            Column("content", css_class="col-lg-8"),
        )

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        order_date = cleaned_data.get("order_date")
        order_due_date = cleaned_data.get("order_due_date")
        estimated_cost = cleaned_data.get("estimated_cost")
        quoted_price = cleaned_data.get("quoted_price")
        security_deposit = cleaned_data.get("security_deposit")
        order_photo = cleaned_data.get("order_photo")

        if not client:
            self.add_error("client", "This field is required.")

        if order_due_date < order_date:
            self.add_error("order_due_date", "Due date cannot be before order date")

        if quoted_price < estimated_cost:
            self.add_error(
                "quoted_price", "Quoted price cannot be less than estimated cost"
            )

        if security_deposit > quoted_price:
            self.add_error(
                "security_deposit",
                "Security deposit cannot be greater than quoted price",
            )

        if quoted_price < 0:
            self.add_error(
                "quoted_price", "Quoted price cannot be negative"
            )

        if estimated_cost < 0:
            self.add_error(
                "estimated_cost", "Estimated cost cannot be negative"
            )

        if security_deposit < 0:
            self.add_error(
                "security_deposit", "Security deposit cannot be negative"
            )

        if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
            self.add_error("order_photo", "File size should not exceed 6 MB.")

        return cleaned_data


class ClientUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Client First Name",
        max_length=50,
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label="Client Last Name",
        max_length=50,
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = PhoneNumberField(
        label="Client Phone Number",
        region="US",
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Client Email Address",
        max_length=254,
        required=False,
        initial=None,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@company.com"}
        ),
    )

    class Meta:
        model = Client
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "email",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ClientUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "g-3"
        self.helper.layout = Layout(
            HTML("""<h1 class="display-6">Update Client</h1>"""),
            Column(
                Column("first_name", css_class="col-lg-10"),
                Column("last_name", css_class="col-lg-10"),
                Column("phone_number", css_class="col-lg-10"),
                Column("email", css_class="col-lg-10"),
            ),
            Submit("submit", value="Submit", css_class="btn btn-primary col-lg-6"),
        )

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        phone_number = cleaned_data.get("phone_number")

        if not first_name:
            self.add_error("first_name", "This field is required.")

        if not last_name:
            self.add_error("last_name", "This field is required.")

        if not phone_number:
            self.add_error("phone_number", "This field is required.")

        return cleaned_data
