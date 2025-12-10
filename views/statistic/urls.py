from django.urls import path, include

urlpatterns = [
    path('group/', include('views.statistic.group.urls')),
]
