from django.urls import path, include
from .list import teacher_schedule_list

urlpatterns = [
    path('list/<int:id>', teacher_schedule_list, name='teacher_schedule_list'),
    # path('schedule/', include('views.teacher.schedule.urls'))
]
