from django.urls import path, include
from .home import home
from .welcome_student import welcome_student
urlpatterns = [
    path('', home, name='home'),
    path('welcome-student', welcome_student, name='welcome_student'),
    path('auth/', include("views.auth.urls")),
    path('setting/', include("views.setting.urls")),
    path('schedule/', include("views.schedule.urls")),
    path('survey/', include("views.survey.urls")),
    path('teacher/', include("views.teacher.urls")),
    path('export-file/', include("views.export_file.urls")),
    # path('setting/', include("views.setting.urls")),
]
