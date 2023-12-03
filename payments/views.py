from django.views.generic import TemplateView
from djstripe.models import Product, Plan
from django.conf import settings
from payments.metadata import product_metadata_dict


class PricingPageView(TemplateView):
    template_name = "payments/pricing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pricing_table_id"] = settings.STRIPE_PRICING_TABLE_ID
        # Replace with Live key in prod
        context["stripe_public_key"] = settings.STRIPE_TEST_PUBLIC_KEY

        # Products context enriched with info from metadata.py
        products = Product.objects.filter(active=True)  # Only active (non-deleted) products
        for product in products:
            product.metadata = product_metadata_dict.get(product.id, None)
        context["products"] = products

        # Plan information
        context["plans"] = Plan.objects.all()

        return context
