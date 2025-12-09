from django.urls import path, include
from .list import export_file_list

urlpatterns = [

    path('list', export_file_list, name='export_file_list')
]
