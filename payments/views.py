from django.views.generic import TemplateView
from djstripe.models import Plan
from django.conf import settings

from payments.metadata import product_metadata_dict


class PricingPageView(TemplateView):
    template_name = "payments/pricing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pricing_table_id"] = settings.STRIPE_PRICING_TABLE_ID
        # Replace with Live key in prod
        context["stripe_public_key"] = settings.STRIPE_TEST_PUBLIC_KEY

        # Price context enriched with product metadata
        plans = Plan.objects.filter(product__active=True)
        for plan in plans:
            plan.product.metadata = product_metadata_dict.get(plan.product.id, None)
            plan.is_default = False

            if plan.id == plan.product.default_price_id:
                plan.is_default = True

        context["plans"] = plans

        return context
