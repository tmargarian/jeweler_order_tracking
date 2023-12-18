from django.urls import path

from .views import UserProfileWizard

app_name = "accounts"

urlpatterns = [
    path("profile_completion/", UserProfileWizard.as_view(), name="profile_completion")
]