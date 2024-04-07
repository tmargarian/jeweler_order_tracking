from django.views.generic import FormView, TemplateView
from .forms import SupportForm
from order_tracking.mixins import CompleteProfileAndActiveSubscriptionMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class LandingPageView(TemplateView):
    template_name = "static_pages/landing.html"


class SupportPageView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, FormView
):
    template_name = "static_pages/support.html"
    context_object_name = "support"
    form_class = SupportForm
