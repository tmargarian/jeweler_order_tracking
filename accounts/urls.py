from django.urls import path

from .views import UserProfileWizard

urlpatterns = [
    path("user_profile/",
         UserProfileWizard.as_view(form_list=UserProfileWizard._form_list,
                                   condition_dict=UserProfileWizard._condition_dict),
         name="user_profile")
]