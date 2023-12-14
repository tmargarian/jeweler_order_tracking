from django import forms
from .models import Order, Client
from django.utils import timezone


class ClientCreateForm(forms.ModelForm):
    client_already_exists = forms.BooleanField(
        label='Existing Client?',
        required=False,
        initial=False,
        widget=forms.Select(
            choices=[
                (True, 'Yes'),
                (False, 'No')
            ],
            attrs={'class': 'form-control'}
        )
    )
    first_name = forms.CharField(
        label='Client First Name',
        max_length=50,
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Client Last Name',
        max_length=50,
        required=False,
        initial=None,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label='Client Phone Number',
        max_length=20,
        required=False,
        initial=None,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Client Email Address',
        max_length=254,
        required=False,
        initial=None,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Client
        fields = (
            "client_already_exists",
            "first_name",
            "last_name",
            "phone_number",
            "email",
        )

    def clean(self):
        cleaned_data = super().clean()
        client_already_exists = cleaned_data.get("client_already_exists")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        phone_number = cleaned_data.get("phone_number")

        if client_already_exists is False:
            if not first_name:
                self.add_error('first_name', "This field is required.")
            if not last_name:
                self.add_error('last_name', "This field is required.")
            if not phone_number:
                self.add_error('phone_number', "This field is required.")

        return cleaned_data


class OrderCreateForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        label='Client',
        queryset=Client.objects.all(),
        required=False,
        initial=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    order_date = forms.DateField(
        label='Order Date',
        widget=forms.DateInput(attrs={'type': 'date', 'format': '%d %b %Y'}),
        required=True,
        initial=timezone.now
    )
    order_due_date = forms.DateField(
        label='Due Date',
        widget=forms.DateInput(attrs={'type': 'date', 'format': '%d %b %Y'}),
        required=True,
        initial=timezone.now
    )
    order_type = forms.ChoiceField(
        label='Order Type',
        choices=[
            ('Purchase', 'Purchase'),
            ('Repair', 'Repair'),
            ('Other', 'Other')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    order_status = forms.ChoiceField(
        label='Status',
        choices=[
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
            ('Canceled', 'Canceled')
        ],
        initial='In Progress',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estimated_cost = forms.DecimalField(
        label='Estimated Cost',
        min_value=0.00,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    quoted_price = forms.DecimalField(
        label='Quoted Price',
        min_value=0.00,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    security_deposit = forms.DecimalField(
        label='Security Deposit',
        min_value=0.00,
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    order_photo = forms.ImageField(
        label='Add Picture',
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*', 'capture': 'camera'})
    )
    note_content = forms.CharField(
        label='Add Note',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )

    class Meta:
        model = Order
        fields = (
            "client",
            "order_date",
            "order_due_date",
            "order_type",
            "order_status",
            "estimated_cost",
            "quoted_price",
            "security_deposit",
            "order_photo",
            "note_content",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OrderCreateForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        user = self.user
        self.fields['client'].queryset = Client.objects \
            .filter(company=user.company) \
            .filter(deleted_flag=False)
        return self.fields['client'].queryset

    def clean(self):
        cleaned_data = super().clean()
        order_date = self.cleaned_data.get('order_date')
        order_due_date = self.cleaned_data.get('order_due_date')
        estimated_cost = self.cleaned_data.get('estimated_cost')
        quoted_price = self.cleaned_data.get('quoted_price')
        security_deposit = self.cleaned_data.get('security_deposit')

        if order_due_date < order_date:
            self.add_error('order_due_date', "Due date cannot be before order date")

        if quoted_price and estimated_cost and quoted_price < estimated_cost:
            self.add_error('quoted_price', "Quoted price cannot be less than estimated cost")

        if quoted_price and security_deposit and security_deposit > quoted_price:
            self.add_error('security_deposit', "Security deposit cannot be greater than quoted price")

        return cleaned_data
