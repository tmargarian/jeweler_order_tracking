from django.views.generic import TemplateView

class LandingPageView(TemplateView):
    template_name = "static_pages/landing.html"
