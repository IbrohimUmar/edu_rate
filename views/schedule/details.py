from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from models.models.schedule import Schedule
# from models.models.schedule_point import SchedulePoint
from models.models.student_meta import StudentMeta


@login_required(login_url='login')
def schedule_details(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    # schedule_point = SchedulePoint.objects.filter(schedule=schedule)

    unregister_students = StudentMeta.objects.filter(group=schedule.group).exclude(user_id__in=list(schedule_point.values_list('student_id', flat=True)))
    return render(request, "schedule/details.html", {
        'schedule': schedule,
        # 'schedule_point': schedule_point,
        'unregister_students': unregister_students,
        'employee': schedule.employee})



