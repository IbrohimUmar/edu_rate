from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('auth/', include('api.auth.urls')),
    path('survey/', include('api.survey.urls')),
    path('schedule/', include('api.schedule.urls')),
    path('schedule-point/', include('api.schedule_point.urls')),
    path('objection/', include('api.objection.urls')),
]
