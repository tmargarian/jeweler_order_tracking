from formtools.wizard.views import SessionWizardView

from .forms import UserProfileForm, CompanyForm
from .models import CustomUser, UserProfile, Company

STEP_ONE = "0"
STEP_TWO = "1"


class UserProfileWizard(SessionWizardView):
    def get_form_instance(self, step):
        instance = None
        created = False

        if step == STEP_ONE:
            instance, created = UserProfile.objects.get_or_create(user_id=self.request.user.id)
        elif step == STEP_TWO:
            custom_user = CustomUser.objects.get(id=self.request.user.id)
            instance, created = Company.objects.get_or_create(id=custom_user.company_id)

        return instance

    def user_profile_incomplete(self):
        profile_instance = self.get_form_instance(STEP_ONE)

        if not profile_instance.first_name or profile_instance.first_name == "":
            return True

        return False

    def return_true(self):
        return True

    _form_list = [(STEP_ONE, UserProfileForm), (STEP_TWO, CompanyForm)]

    _condition_dict = {STEP_ONE: user_profile_incomplete, STEP_TWO: return_true}
