from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "my_app/home_page.html"
