import datetime
import random

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from models.models.schedule import Schedule
from models.models.schedule_point import SchedulePoint
from models.models.student_meta import StudentMeta
from models.models.user import User
from services.schedule.schedule_point import calculate_deadline, calculate_lesson_end_time


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


    # SchedulePoint.objects.exclude(is_teacher_present='0').update(is_submit_notification=True)

    #
    # from django.utils import timezone
    # from datetime import timedelta
    #
    # today = timezone.now()
    # three_days_ago = today - timedelta(days=3)
    # schedules = Schedule.objects.filter(lesson_date__gte=three_days_ago)
    # print(schedules.count())
    # from django.utils import timezone
    #
    # random_number = random.randint(1, 10)
    # print(random_number)
    # ta = schedules.count()
    # for schedule in schedules:
    #     ta -=1
    #     print(ta)
    #     random_number = random.randint(1,10)
    #     if random_number > 3:
    #         students = StudentMeta.objects.filter(group=schedule.group)
    #         for s in students:
    #             random_fot_st = random.randint(1,10)
    #             if random_fot_st <= 2:
    #                 SchedulePoint.objects.create(
    #                     student=s.user,
    #                     schedule=schedule,
    #                     employee=schedule.employee,
    #                     submission_deadline=calculate_deadline(
    #                             schedule.lesson_date, schedule.lesson_pair.start_time
    #                         ),
    #                     notification_planned_date=calculate_lesson_end_time(
    #                             schedule.lesson_date, schedule.lesson_pair.end_time
    #                         ),
    #                     is_teacher_present='2',
    #                     notification_sent_at=timezone.now(),
    #                     answer_submitted_at=timezone.now()
    #                 )
    #             elif random_fot_st == '3':
    #                 continue
    #             else:
    #
    #                 SchedulePoint.objects.create(
    #                     student=s.user,
    #                     schedule=schedule,
    #                     employee=schedule.employee,
    #                     submission_deadline=calculate_deadline(
    #                             schedule.lesson_date, schedule.lesson_pair.start_time
    #                         ),
    #                     notification_planned_date=calculate_lesson_end_time(
    #                             schedule.lesson_date, schedule.lesson_pair.end_time
    #                         ),
    #                     is_teacher_present='1',
    #                     teacher_speech_and_culture=str(random.randint(1,3)),
    #                     topic_practical_relevance=str(random.randint(1,2)),
    #                     lesson_feedback=str(random.randint(1,3)),
    #
    #                     notification_sent_at=timezone.now(),
    #                     answer_submitted_at=timezone.now()
    #                 )



    return render(request, 'home.html', {"schedule_point":schedule_point,
                                                            "user_statistic":user_statistic})
