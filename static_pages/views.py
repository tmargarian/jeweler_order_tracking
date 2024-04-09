from django.views.generic import FormView, TemplateView
from .forms import SupportForm
from order_tracking.mixins import CompleteProfileAndActiveSubscriptionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Email
from django.core.mail import send_mail
from django.conf import settings


class LandingPageView(TemplateView):
    template_name = "static_pages/landing.html"


class SupportPageView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, FormView
):
    template_name = "static_pages/support.html"
    context_object_name = "support"
    form_class = SupportForm
    success_url = reverse_lazy("static_pages:support")

    def form_valid(self, form):
        # Gather form data
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        phone_number = form.cleaned_data['phone_number']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        # Compose email subject and message body
        subject = 'Support Request from {}'.format(email)
        message_body = f'Name: {first_name} {last_name}\nPhone Number: {phone_number}\nEmail: {email}\nMessage: {message}'

        # Send email
        send_mail(
            subject,
            message_body,
            email,  # From email address
            [settings.EMAIL_HOST_USER],  # To email addresses
            fail_silently=False,
        )

        # You can add additional logic here, such as displaying a success message
        # or redirecting to another page.

        return super().form_valid(form)
