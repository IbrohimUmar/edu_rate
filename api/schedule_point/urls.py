from django.urls import path, include
from .views import SchedulePointUpdateAPIView


urlpatterns = [
    path('update/', SchedulePointUpdateAPIView.as_view()),

]
