from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin

from djstripe.models import Subscription
from accounts.models import UserProfile, Company


class CompleteProfileAndActiveSubscriptionMixin(UserPassesTestMixin):
    """Mixin to use in the app views to filter only customers with completed
    UserProfile and Company fields"""

    def __init__(self):
        self.incomplete_profile = None
        self.subscription_missing = None
        self.subscription_inactive = None

    def test_func(self):
        # Checking for user profile completion
        try:
            user_profile = UserProfile.objects.get(user_id=self.request.user.id)
        except UserProfile.DoesNotExist:
            self.incomplete_profile = True
            return False

        if (
            not user_profile.first_name
            or not user_profile.last_name
            or not user_profile.phone_number
        ):
            complete_user_profile = False
        else:
            complete_user_profile = True

        # Checking for company profile completion
        company_profile = self.request.user.company
        if (
            not company_profile.company_name
            or not company_profile.address_lines
            or not company_profile.city
            or not company_profile.state
            or not company_profile.zip_code
        ):
            complete_company_profile = False
        else:
            complete_company_profile = True

        # Checking profile completeness
        if not complete_user_profile or not complete_company_profile:
            self.incomplete_profile = True
            return False

        # Checking for subscription status
        company = Company.objects.get(owner__user_id=self.request.user.id)

        try:
            subscription = Subscription.objects.get(customer__subscriber_id=company.id)
        except Subscription.DoesNotExist:
            # Creating an attribute for the object to signal missing subscription
            self.subscription_missing = True
            print("subscription_does_not_exist")
            return False

        if subscription.status not in ["active", "trialing"]:
            self.subscription_inactive = True
            print("subscription_inactive")
            return False

        return (
            complete_user_profile
            and complete_company_profile
            and subscription.status in ["active", "trialing"]
        )

    def handle_no_permission(self):
        # if the subscription is active it must be the incomplete profile
        if self.incomplete_profile:
            return redirect("accounts:profile_completion")
        # check if the subscription is missing
        elif self.subscription_missing:
            print("a")
            return redirect("pricing_page_logged_in")
        # check if the subscription is inactive
        elif self.subscription_inactive:
            print("b")
            return redirect("pricing_page_logged_in")
        else:
            return super().handle_no_permission()
