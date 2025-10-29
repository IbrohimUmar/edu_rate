from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from models.models.employee_meta import EmployeeMeta
from models.models.schedule import Schedule
from models.models.schedule_point import SchedulePoint
from models.models.student_meta import StudentMeta
from models.models.user import User


@login_required(login_url='login')
def teacher_details(request, id):
    teacher = get_object_or_404(User, id=id, type='2')
    employee_metas = EmployeeMeta.objects.filter(user=teacher)
    return render(request, "teacher/details.html", {
        'teacher': teacher,
        'employee_metas': employee_metas})



