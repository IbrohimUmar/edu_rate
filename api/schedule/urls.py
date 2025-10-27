from django.urls import path, include
from .views import ScheduleListView, ScheduleDetailByIdView

urlpatterns = [
    path('', ScheduleListView.as_view()),
    path('details/', ScheduleDetailByIdView.as_view()),
]
