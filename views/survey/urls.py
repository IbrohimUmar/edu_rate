from django.urls import path, include
from .list import survey_list
from .detail import survey_detail

urlpatterns = [
    path('list', survey_list, name='survey_list'),
    path('detail/<int:id>', survey_detail, name='survey_detail')
]
