from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from formtools.wizard.views import SessionWizardView


from .forms import UserProfileForm, CompanyForm
from .models import UserProfile, Company

STEP_ONE = "0"
STEP_TWO = "1"

TEMPLATES = {
    STEP_ONE: "account/profile_completion/user_profile.html",
    STEP_TWO: "account/profile_completion/company_profile.html",
}


class UserProfileWizard(SessionWizardView):
    form_list = [(STEP_ONE, UserProfileForm), (STEP_TWO, CompanyForm)]

    # Setting the instance_dict and condition_dict
    def dispatch(self, request, *args, **kwargs):
        user_profile_instance = UserProfile.objects.get(user_id=self.request.user.id)
        company_instance = Company.objects.get(id=self.request.user.company_id)

        self.instance_dict = {
            STEP_ONE: user_profile_instance,
            STEP_TWO: company_instance,
        }

        return super(UserProfileWizard, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_instance(self, step):
        return self.instance_dict.get(step, None)

    def done(self, form_list, **kwargs):
        for form in form_list:
            if isinstance(form, UserProfileForm):
                user_profile = form.save(self.request)
                user_profile.save()
            elif isinstance(form, CompanyForm):
                company_profile = form.save(self.request)
                company_profile.save()
        return redirect("order_list")

    def user_profile_incomplete(self):
        profile_instance = self.get_form_instance(STEP_ONE)

        if (  # Checking if any of the profile fields is empty -> Trigger form
            not profile_instance.first_name
            or not profile_instance.last_name
            or not profile_instance.phone_number
        ):
            return True

        return False

    def company_incomplete(self):
        company_instance = self.get_form_instance(STEP_TWO)

        if (
            not company_instance.company_name
            or not company_instance.address_lines
            or not company_instance.city
            or not company_instance.state
            or not company_instance.zip_code
        ):
            return True

        return False

    condition_dict = {
        STEP_ONE: user_profile_incomplete,
        STEP_TWO: company_incomplete,
    }
