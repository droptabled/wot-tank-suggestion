from django.urls import path

from . import views

app_name = 'suggestions'

urlpatterns = [
    path('maintenance', views.maintenance),
    path('explore', views.explore),
    path('root_tank', views.root_tank),
    path('improve_tank', views.improve_tank)
]