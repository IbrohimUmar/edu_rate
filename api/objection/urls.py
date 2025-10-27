from django.urls import path, include
from .views import StudentObjectionAPIView
urlpatterns = [
    path('create/', StudentObjectionAPIView.as_view()),
]
