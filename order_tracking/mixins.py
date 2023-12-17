from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.models import UserProfile

class ProfileCompletionRequiredMixin(UserPassesTestMixin):
    """Mixin to use in the app views to filter only customers with completed
       UserProfile and Company fields"""

    def test_func(self):
        complete_user_profile = True

        user_profile = UserProfile.objects.get(user_id=self.request.user.id)

        if (
            not user_profile.first_name
            or not user_profile.last_name
            or not user_profile.phone_number
        ):
            complete_user_profile = False

        complete_company_profile = True
        company_profile = self.request.user.company
        if (
            not company_profile.company_name
            or not company_profile.address_lines
            or not company_profile.city
            or not company_profile.state
            or not company_profile.zip_code

        ):
            complete_company_profile = False

        return complete_user_profile and complete_company_profile

    def handle_no_permission(self):
        return redirect(reverse('accounts:profile_completion'))
