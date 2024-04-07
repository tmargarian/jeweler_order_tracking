from django.urls import path

from .views import LandingPageView, SupportPageView

app_name = "static_pages"

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing"),
    path("support", SupportPageView.as_view(), name="support"),
]
