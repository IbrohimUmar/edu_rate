from django.urls import path, include
from .list import schedule_list

urlpatterns = [
    path('list', schedule_list, name='schedule_list')
]
