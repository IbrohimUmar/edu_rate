from django.urls import path, include
from .registered import statistic_group_registered

urlpatterns = [
    path('registred', statistic_group_registered, name='statistic_group_registered')
]
