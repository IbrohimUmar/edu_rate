from django.urls import path, include
from .list import survey_schedule_list

urlpatterns = [
    path('list/<int:id>', survey_schedule_list, name='survey_schedule_list'),
]
