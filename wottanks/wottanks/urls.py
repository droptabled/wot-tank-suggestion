from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('statparser/', include('statparser.urls')),
    path('suggestions/', include('suggestions.urls'))
]
