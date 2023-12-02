from django.urls import path

from .views import PricingPageView

urlpatterns = [
    path("pricing", PricingPageView.as_view(), name="pricing_page")
]
