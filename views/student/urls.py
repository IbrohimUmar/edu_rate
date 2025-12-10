from django.urls import path, include
from .list import student_list
from .details import student_details
urlpatterns = [
    path('list', student_list, name='student_list'),
    path('details/<int:id>', student_details, name='student_details'),
]
