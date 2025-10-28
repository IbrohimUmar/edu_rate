from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from models.models.schedule_point import SchedulePoint
from models.models.user import User


@login_required(login_url='login')
def home(request):
    user_statistic = User.objects.filter(type='3').aggregate(
        total_student_count=Count("id"),
        total_registered_count=Count("id", Q(telegram_id__isnull=False)),
    )
    schedule_point = SchedulePoint.objects.aggregate(
        total_answers_count=Count("id", filter=~Q(is_teacher_present='0')),
        total_send_notify_count=Count("id", filter=Q(is_submit_notification=True)),
    )
    return render(request, 'home.html', {"schedule_point":schedule_point,
                                                            "user_statistic":user_statistic})
