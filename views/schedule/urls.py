from django.urls import path, include
from .list import schedule_list
from .details import schedule_details

urlpatterns = [
    path('list', schedule_list, name='schedule_list'),
    path('details/<int:id>', schedule_details, name='schedule_details')
]
