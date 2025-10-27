from django.urls import path, include
from .views import CheckActivationApiViews, ActivationApiViews

urlpatterns = [
    path('activation/', ActivationApiViews.as_view()),
    path('check-activation/', CheckActivationApiViews.as_view()),
]
