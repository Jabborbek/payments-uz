from django.urls import path

from uzum.views import UzumWebHookAPIView

urlpatterns = [
    path("<str:action>/", UzumWebHookAPIView.as_view()),
]
