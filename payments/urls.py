from django.urls import path

from .views import PricingPageView, PricingPageLoggedInView, SubscriptionConfirmView

urlpatterns = [
    path("pricing", PricingPageView.as_view(), name="pricing_page"),
    path("pricing-logged-in", PricingPageLoggedInView.as_view(), name="pricing_page_logged_in"),
    path("subscription-confirm/", SubscriptionConfirmView.as_view(), name="subscription_confirm"),
]