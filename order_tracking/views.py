from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "order_tracking/home.html"