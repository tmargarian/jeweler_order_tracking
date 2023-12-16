from django.urls import path

from .views import UserProfileWizard

urlpatterns = [
    path("user_profile/", UserProfileWizard.as_view(), name="profile")
]