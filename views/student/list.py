from threading import Thread

from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from models.models.meta import Group
from models.models.user import User
from services.export_file.student.format1.manager import export_students_manager


def unregister_student(students_qs, responsible):
    for s in students_qs:
        meta = s.student
        is_register = "Ro'yxatdan o'tgan" if s.telegram_id is not None else "Ro'yxatdan o'tmagan"
        print(f'{s.hemis_id_number}, {s.full_name}, {meta.department.name}, {meta.group.name}, {is_register}')




@login_required(login_url='login')
def student_list(request):
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)

    export_to_excel = request.GET.get('export') == 'excel'
    users_qs = User.objects.filter(type='3').order_by('-id')
    if search_query:
        users_qs = users_qs.filter(full_name__icontains=search_query)

    is_registered = request.GET.get('is_registered', '0')
    if is_registered != '0':
        if is_registered == '1':
            users_qs = users_qs.filter(telegram_id__isnull=False)
        elif is_registered == '2':
            users_qs = users_qs.filter(telegram_id__isnull=True)
    group_id = int(request.GET.get('group_id') or 0)
    if group_id != 0:
        users_qs = users_qs.filter(student__group_id=group_id)

    if export_to_excel:
        # data = export_file_schedule_format1_data_format(schedules, survey)
        # return export_file_schedule_format1_export_excel(data, survey)
        thread = Thread(
            target=export_students_manager,
            args=(users_qs, request.user)
        )
        thread.start()
        # unregister_student(users_qs, request.user)
        # thread = Thread(target=export_file_schedule_format1_manager, args=(schedules, survey, request.user))
        # thread.start()
        messages.success(request, "Faylga eksport qilinmoqda..")
        return redirect('student_list')

    group_qs = Group.objects.filter(is_active=True).order_by('-id')
    paginator = Paginator(users_qs, 50)  # sahifada 25 ta qator
    queryset = paginator.get_page(page)  # ← SENING HTML'DAGI NOM
    queryset_count = paginator.count     # ← umumiy ma'lumotlar soni
    context = {
        'queryset': queryset,
        'queryset_count': queryset_count,
        'group_qs': group_qs,
    }
    return render(request, "student/list.html", context)
