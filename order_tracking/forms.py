from django import forms
from django.utils import timezone
from .models import Order, Client
from crispy_forms.helper import FormHelper


class OrderCreateForm(forms.ModelForm):
    client_already_exists = forms.BooleanField(
        label='Existing Client?',
        required=False, initial=False,
        widget=forms.Select(choices=[(True, 'Yes'), (False, 'No')], attrs={'class': 'form-control'}))
    first_name = forms.CharField(
        label='Client First Name',
        max_length=50, required=False, initial=None, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        label='Client Last Name',
        max_length=50, required=False, initial=None, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(
        label='Client Phone Number',
        max_length=20, required=False, initial=None, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(
        label='Client Email Address',
        max_length=254, required=False, initial=None, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    client = forms.ModelChoiceField(
        label='Client',
        queryset=Client.objects.all(),
        required=False, initial=None, widget=forms.Select(attrs={'class': 'form-control'}))
    order_type = forms.ChoiceField(
        label='Order Type',
        choices=[('Purchase', 'Purchase'), ('Repair', 'Repair'), ('Other', 'Other')],
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    order_status = forms.ChoiceField(
        label='Order Status',
        choices=[('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    order_date = forms.DateField(
        label='Order Date',
        required=False, widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)
    order_due_date = forms.DateField(
        label='Due Date',
        required=False, widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)
    estimated_cost = forms.DecimalField(
        label='Estimated Cost',
        min_value=0.00, max_value=1000000.00, max_digits=10, decimal_places=2, initial=0.00, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    quoted_price = forms.DecimalField(
        label='Quoted Price',
        min_value=0.00, max_value=1000000.00, max_digits=10, decimal_places=2, initial=0.00, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    security_deposit = forms.DecimalField(
        label='Security Deposit',
        min_value=0.00, max_value=1000000.00, max_digits=10, decimal_places=2, initial=0.00, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    order_photo = forms.ImageField(
        label='Add Picture',
        required=False, widget=forms.FileInput(attrs={'accept': 'image/*', 'capture': 'camera'}))
    content = forms.CharField(label='Add Note', widget=forms.Textarea(attrs={'rows': 2}), required=False)

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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.get_filtered_clients(user)

    def get_filtered_clients(self, user):
        if user and user.is_authenticated:
            return Client.objects.filter(
                company=user.company,
                deleted_flag=False
            )
        return Client.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        client_already_exists = cleaned_data.get("client_already_exists")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        phone_number = cleaned_data.get("phone_number")
        client = cleaned_data.get("client")
        order_date = cleaned_data.get('order_date')
        order_due_date = cleaned_data.get('order_due_date')
        estimated_cost = cleaned_data.get('estimated_cost')
        quoted_price = cleaned_data.get('quoted_price')
        security_deposit = cleaned_data.get('security_deposit')
        order_photo = cleaned_data.get('order_photo')

        if client_already_exists is False:
            if not first_name:
                self.add_error('first_name', "This field is required.")

            if not last_name:
                self.add_error('last_name', "This field is required.")

            if not phone_number:
                self.add_error('phone_number', "This field is required.")

        if client_already_exists is True:
            if not client:
                self.add_error('client', "This field is required.")

        if order_due_date < order_date:
            self.add_error('order_due_date', "Due date cannot be before order date")

        if quoted_price < estimated_cost:
            self.add_error('quoted_price', "Quoted price cannot be less than estimated cost")

        if security_deposit > quoted_price:
            self.add_error('security_deposit', "Security deposit cannot be greater than quoted price")

        if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
            self.add_error("order_photo", "File size should not exceed 6 MB.")

        return cleaned_data


class OrderUpdateForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        label='Client',
        queryset=Client.objects.all(),
        required=False, initial=None, widget=forms.Select(attrs={'class': 'form-control'}))
    order_type = forms.ChoiceField(
        label='Order Type',
        choices=[('Purchase', 'Purchase'), ('Repair', 'Repair'), ('Other', 'Other')],
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    order_status = forms.ChoiceField(
        label='Order Status',
        choices=[('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    order_date = forms.DateField(
        label='Order Date',
        required=False, widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)
    order_due_date = forms.DateField(
        label='Due Date',
        required=False, widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)
    estimated_cost = forms.DecimalField(
        label='Estimated Cost',
        min_value=0.00, max_value=1000000.00, max_digits=10, decimal_places=2, initial=0.00, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    quoted_price = forms.DecimalField(
        label='Quoted Price',
        min_value=0.00, max_value=1000000.00, max_digits=10, decimal_places=2, initial=0.00, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    security_deposit = forms.DecimalField(
        label='Security Deposit',
        min_value=0.00, max_value=1000000.00, max_digits=10, decimal_places=2, initial=0.00, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    order_photo = forms.ImageField(
        label='Add Picture',
        required=False, widget=forms.FileInput(attrs={'accept': 'image/*', 'capture': 'camera'}))
    content = forms.CharField(label='Add Note', widget=forms.Textarea(attrs={'rows': 2}), required=False)

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        user = self.user
        self.fields['client'].queryset = Client.objects \
            .filter(company=user.company) \
            .filter(deleted_flag=False)
        return self.fields['client'].queryset

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        order_date = cleaned_data.get('order_date')
        order_due_date = cleaned_data.get('order_due_date')
        estimated_cost = cleaned_data.get('estimated_cost')
        quoted_price = cleaned_data.get('quoted_price')
        security_deposit = cleaned_data.get('security_deposit')
        order_photo = cleaned_data.get('order_photo')

        if not client:
            self.add_error('client', "This field is required.")

        if order_due_date < order_date:
            self.add_error('order_due_date', "Due date cannot be before order date")

        if quoted_price < estimated_cost:
            self.add_error('quoted_price', "Quoted price cannot be less than estimated cost")

        if security_deposit > quoted_price:
            self.add_error('security_deposit', "Security deposit cannot be greater than quoted price")

        if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
            self.add_error("order_photo", "File size should not exceed 6 MB.")

        return cleaned_data


class ClientUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Client First Name',
        max_length=50, required=False, initial=None, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        label='Client Last Name',
        max_length=50, required=False, initial=None, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(
        label='Client Phone Number',
        max_length=20, required=False, initial=None, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(
        label='Client Email Address',
        max_length=254, required=False, initial=None, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Client
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "email",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ClientUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        phone_number = cleaned_data.get("phone_number")

        if not first_name:
            self.add_error('first_name', "This field is required.")

        if not last_name:
            self.add_error('last_name', "This field is required.")

        if not phone_number:
            self.add_error('phone_number', "This field is required.")

        return cleaned_data
