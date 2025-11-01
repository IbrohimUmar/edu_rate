from django.urls import path, include
from .home import home
urlpatterns = [
    path('', home, name='home'),
    path('auth/', include("views.auth.urls")),
    path('setting/', include("views.setting.urls")),
    path('schedule/', include("views.schedule.urls")),
    path('survey/', include("views.survey.urls")),
    path('teacher/', include("views.teacher.urls")),
    # path('setting/', include("views.setting.urls")),
]
