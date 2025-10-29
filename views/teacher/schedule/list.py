import io, datetime
import random
import tempfile

from django.db.models import Q, Count, Sum, F, OuterRef, Subquery, Case, Value, FloatField, When, IntegerField
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from openpyxl import Workbook
from openpyxl.formatting.rule import DataBarRule, ColorScaleRule
from openpyxl.styles import Alignment, Font, Side, Border
from openpyxl.worksheet.cell_range import CellRange

from django.core.paginator import Paginator
from django.utils.timezone import now

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from models.models.schedule import Schedule
from django.db.models import Count, Q

from models.models.schedule_point import SchedulePoint
from models.models.user import User
from views.schedule.list import export_schedule_to_excel


@login_required(login_url='login')
def teacher_schedule_list(request, id):
    teacher = get_object_or_404(User, id=id, type='2')
    search_query = request.GET.get('search', '').strip()
    export_to_excel = request.GET.get('export') == 'excel'
    selected_date = None
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()

    # schedules = Schedule.objects.filter(employee=teacher,
    #                                     lesson_date__date=selected_date
    #                                     ).order_by('lesson_date')
    schedules = Schedule.objects.filter(employee=teacher).order_by('-lesson_date')

    if date_str:
        schedules = schedules.filter(lesson_date__date=selected_date)

    schedules = (
        schedules
        .annotate(
            group_student_count_qs=Count("group__student", distinct=True),
            answer_send_count_qs=Count(
                "schedulepoint",
                filter=~Q(schedulepoint__is_teacher_present="0"),  # sadece cevap gönderenler
                distinct=True
            )
        )
    )
    send_answer_type = request.GET.get("send_answer", '0')
    if send_answer_type != '0':
        if send_answer_type == '1':
            schedules = schedules.filter(answer_send_count_qs__gt=0)
        else:
            schedules = schedules.exclude(answer_send_count_qs__gt=0)
    if search_query:
        schedules = schedules.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__second_name__icontains=search_query) |
            Q(employee__third_name__icontains=search_query)
        )
    if export_to_excel:
        return export_schedule_to_excel(schedules)

    page = request.GET.get('page', 1)
    paginator = Paginator(schedules, 50)  # sahifada 25 ta qator
    queryset = paginator.get_page(page)  # ← SENING HTML'DAGI NOM
    queryset_count = paginator.count     # ← umumiy ma'lumotlar soni
    context = {
        'queryset': queryset,
        'queryset_count': queryset_count,
        'selected_date': selected_date
    }
    return render(request, "teacher/schedule/list.html", context)
