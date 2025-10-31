from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from models.models.user import User


@login_required(login_url='login')
def home(request):
    user_statistic = User.objects.filter(type='3').aggregate(
        total_student_count=Count("id"),
        total_registered_count=Count("id", Q(telegram_id__isnull=False)),
    )
    return render(request, 'home.html', {"schedule_point": {'total_answers_count':0, 'total_send_notify_count':0},
                                                            "user_statistic":user_statistic})
