from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.models import UserProfile


class CompleteProfileMixin(UserPassesTestMixin):
    """Mixin to use in the app views to filter only customers with completed
    UserProfile and Company fields"""

    def __init__(self):
        self.incomplete_profile = None

    def test_func(self):
        # Checking for user profile completion
        user_profile = UserProfile.objects.get(user_id=self.request.user.id)

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

        print(f"Company Profile Complete: {complete_company_profile} \n"
              f"User Profile Complete: {complete_user_profile}")

        # Checking profile completeness
        if not complete_user_profile or not complete_company_profile:
            self.incomplete_profile = True
            return False
        else:
            return True

    def handle_no_permission(self):
        # if the subscription is active it must be the incomplete profile
        if self.incomplete_profile:
            return redirect("accounts:profile_completion")
