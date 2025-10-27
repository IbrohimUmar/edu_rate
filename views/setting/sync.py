from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from models.models.student_meta import StudentMeta
from models.models.employee_meta import EmployeeMeta
from services.sync_hemis.employee import employee_sync
from services.sync_hemis.schedule import schedule_sync
from services.sync_hemis.student import student_sync


@login_required(login_url='login')
def setting_sync(request):
    sync_employee = request.GET.get('sync_employee', None)
    if sync_employee is not None:
        employee_sync()
        messages.success(request, "O'qituvchilar sinxronlandi")

    sync_student = request.GET.get('sync_student', None)
    if sync_student is not None:
        student_sync()
        messages.success(request, "Talabalar sinxronlandi")

    sync_schedule = request.GET.get('sync_schedule', None)
    if sync_schedule is not None:
        schedule_sync()
        messages.success(request, "O'quv rejalar sinxronlandi")
    print(request.GET)

    if request.GET:
        return redirect("setting_sync")

    return render(request, 'setting/sync.html')
