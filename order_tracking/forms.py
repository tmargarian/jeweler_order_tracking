from django import forms
from .models import Order, Client, Note


class ClientCreateForm(forms.ModelForm):
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
            if first_name is None:
                self.add_error('first_name', "This field is required.")
            if last_name is None:
                self.add_error('last_name', "This field is required.")
            if phone_number is None:
                self.add_error('phone_number', "This field is required.")

        return cleaned_data


class OrderCreateForm(forms.ModelForm):
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

        if quoted_price < estimated_cost:
            self.add_error('quoted_price', "Quoted price cannot be less than estimated cost")

        if security_deposit > quoted_price:
            self.add_error('security_deposit', "Security deposit cannot be greater than quoted price")

        return cleaned_data


class NoteCreateForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = (
            "content",
        )
