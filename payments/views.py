from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import redirect, render

from payments.metadata import product_metadata_dict
from djstripe.models import Plan, Subscription, Customer
from djstripe.settings import djstripe_settings
from accounts.models import Company
from .mixins import CompleteProfileMixin

import stripe


class PricingPageView(TemplateView):
    template_name = "payments/pricing_page.html"

    def get_context_data(self, **kwargs):
        # Price context enriched with product metadata
        plans = Plan.objects.filter(product__active=True)
        for plan in plans:
            plan.product.metadata = product_metadata_dict.get(plan.product.id, None)
            plan.is_default = False

            if plan.id == plan.product.default_price_id:
                plan.is_default = True

        context = super().get_context_data(**kwargs)
        context["plans"] = plans

        return context


class PricingPageLoggedInView(LoginRequiredMixin, CompleteProfileMixin, TemplateView):
    template_name = "payments/pricing_page_logged_in.html"

    # Show the subscription page only in case the customer is logged in and subscription is dead
    def dispatch(self, request, *args, **kwargs):
        # Logged in check
        if not request.user.id:
            return super().dispatch(request, *args, **kwargs)

        try:
            subscription = Subscription.objects.get(customer__company__owner__user_id=request.user.id)
        except Subscription.DoesNotExist:
            return super().dispatch(request, *args, **kwargs)

        if subscription.status not in ["incomplete_expired", "canceled", "unpaid"]:
            return redirect("https://billing.stripe.com/p/login/test_fZeeYk74mdw2cda144")

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pricing_table_id"] = settings.STRIPE_PRICING_TABLE_ID
        # Replace with Live key in prod
        context["stripe_public_key"] = settings.STRIPE_TEST_PUBLIC_KEY

        company = Company.objects.get(owner__user_id=self.request.user.id)
        context["company_id"] = company.id

        return context


class SubscriptionConfirmView(LoginRequiredMixin, TemplateView):
    template_name = "payments/subscription_confirm.html"

    def get(self, request, *args, **kwargs):
        stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY

        session_id = request.GET.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)

        company_id = int(session.client_reference_id)
        session_company = Company.objects.get(id=company_id)
        current_company = Company.objects.get(owner__user_id=request.user.id)

        if session_company != current_company:
            print("There was an error with your subscription. Please contact support.")
            return redirect("landing")

        # Retrieving the object
        customer = Customer.objects.get(id=session.customer)
        subscription = Subscription.objects.get(customer_id=customer.id)

        # Updating the object
        customer.default_payment_method = subscription.default_payment_method
        customer.subscriber = session_company
        session_company.subscription_id = subscription
        session_company.customer = customer

        # Saving the objects
        customer.save()
        session_company.save()

        return render(request, self.template_name)
