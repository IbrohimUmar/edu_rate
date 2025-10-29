from django.urls import path, include
from .list import teacher_list
from .details import teacher_details

urlpatterns = [
    path('list', teacher_list, name='teacher_list'),
    path('details/<int:id>', teacher_details, name='teacher_details'),
    path('schedule/', include('views.teacher.schedule.urls'))
]
