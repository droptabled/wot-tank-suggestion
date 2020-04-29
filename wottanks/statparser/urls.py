from django.urls import path

from . import views

app_name = 'statparser'

urlpatterns = [
    path('scrapestart', views.scrapestart, name='scrapestart'),
    path('scrapeall', views.scrapeall, name='scrapeall')
]