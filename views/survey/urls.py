from django.urls import path, include
from .list import survey_list
from .detail import survey_detail
from .create import survey_create

urlpatterns = [
    path('list', survey_list, name='survey_list'),
    path('detail/<int:id>', survey_detail, name='survey_detail'),
    path('create/<int:id>', survey_create, name='survey_create')
]
