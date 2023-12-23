from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse
from formtools.wizard.views import SessionWizardView


from .forms import UserProfileForm, CompanyForm
from .models import UserProfile, Company, ZipToAddressLookup

STEP_ONE = "0"
STEP_TWO = "1"

TEMPLATES = {
    STEP_ONE: "account/profile_completion/user_profile.html",
    STEP_TWO: "account/profile_completion/company_profile.html",
}


class UserProfileWizard(SessionWizardView):
    form_list = [(STEP_ONE, UserProfileForm), (STEP_TWO, CompanyForm)]

    # Setting the instance_dict
    def dispatch(self, request, *args, **kwargs):
        user_profile_instance = UserProfile.objects.get(user_id=self.request.user.id)
        company_instance = Company.objects.get(id=self.request.user.company_id)

        self.instance_dict = {
            STEP_ONE: user_profile_instance,
            STEP_TWO: company_instance,
        }

        return super(UserProfileWizard, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # AJAX handling for City/State autocomplete using Zip Code
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if is_ajax:
            zip_code = request.headers.get("zipCode")
            address = ZipToAddressLookup.objects.get(zip=zip_code)
            return JsonResponse({"city": address.city, "state": address.state_short})

        get_response = super().get(request, *args, **kwargs)
        return get_response

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_instance(self, step):
        return self.instance_dict.get(step, None)

    # Need this to save the data on each step
    def render_goto_step(self, goto_step, **kwargs):
        """We can't move to second step if the first one is incomplete,
        but we can move back to first step with the second one incomplete.
        Submission should be possible with both forms valid."""

        # Current step form
        form = self.get_form(
            step=self.steps.current, data=self.request.POST, files=self.request.FILES
        )

        # On the first step - render the same form if it's invalid
        if self.steps.current == STEP_ONE and not form.is_valid():
            return self.render(form, **kwargs)

        # For both steps (first step | valid only; second step | valid or invalid)
        # Save the current step data and files
        self.storage.set_step_data(self.steps.current, self.process_step(form))
        self.storage.set_step_files(self.steps.current, self.process_step_files(form))

        # Move to next step
        self.storage.current_step = goto_step
        form = self.get_form(
            data=self.storage.get_step_data(self.steps.current),
            files=self.storage.get_step_files(self.steps.current),
        )

        return self.render(form, **kwargs)

    def done(self, form_list, **kwargs):
        for form in form_list:
            if isinstance(form, UserProfileForm):
                user_profile = form.save()
                user_profile.save()
            elif isinstance(form, CompanyForm):
                company_profile = form.save()
                company_profile.save()
        return redirect(reverse("order_tracking:order_list"))
