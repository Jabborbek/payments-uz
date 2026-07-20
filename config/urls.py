from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("payme/", include("payme.urls")),
    path("uzum/", include("uzum.urls")),
]
