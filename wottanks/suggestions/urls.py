from django.urls import path

from . import views

app_name = 'suggestions'

urlpatterns = [
    path('test', views.test)
]