from django.views.generic import TemplateView
from djstripe.models import Product
from django.conf import settings


class PricingPageView(TemplateView):
    template_name = "payments/pricing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pricing_table_id"] = settings.STRIPE_PRICING_TABLE_ID
        context["stripe_public_key"] = settings.STRIPE_TEST_PUBLIC_KEY  # Replace with Live key in prod
        context["products"] = Product.objects.all()
        return context
