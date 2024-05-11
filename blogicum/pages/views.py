from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


# def about(request):
#     template = 'pages/about.html'
#     return render(request, template)


# def rules(request):
#     template = 'pages/rules.html'
#     return render(request, template)
