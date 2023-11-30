from django.views.generic import TemplateView

class PricingPageView(TemplateView):
    template_name = "payments/pricing_page.html"