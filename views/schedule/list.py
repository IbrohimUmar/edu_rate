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
from django.shortcuts import render

from models.models.schedule import Schedule
from django.db.models import Count, Q

from models.models.schedule_point import SchedulePoint


@login_required(login_url='login')
def schedule_list(request):
    search_query = request.GET.get('search', '').strip()
    export_to_excel = request.GET.get('export') == 'excel'
    date_str = request.GET.get('date')
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()
    except ValueError:
        selected_date = now().date()  # noto‘g‘ri format bo‘lsa, bugungi kun
    schedules = Schedule.objects.filter(
                                        lesson_date__date=selected_date
                                        ).order_by('lesson_date')
    schedules = (
        # Schedule.objects.all()
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


    # from models.models.student_meta import StudentMeta
    # print(random.randint(1, 4))
    # for schedule in schedules:
    #     student_meta = StudentMeta.objects.filter(group=schedule.group)
    #     for student in student_meta:
    #         SchedulePoint.objects.create(
    #             schedule=schedule,
    #             student=student.user,
    #             employee=schedule.employee,
    #             is_teacher_present='1',
    #             teacher_speech_and_culture=str(random.randint(1,3)),
    #             topic_practical_relevance=str(random.randint(1,2)),
    #             lesson_feedback=str(random.randint(1,3)),
    #
    #             is_submit_notification=True,
    #             notification_planned_date=datetime.datetime.now(),
    #             submission_deadline=datetime.datetime.now(),
    #             notification_sent_at=datetime.datetime.now(),
    #             answer_submitted_at=datetime.datetime.now(),
    #         )
    #
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
    return render(request, "schedule/list.html", context)

def export_schedule_to_excel(schedules):
    schedules_id = list(schedules.values_list('id', flat=True))
    wb = Workbook()
    ws = wb.active
    ws.title = "Schedule KPI"

    # --- ÜST BAŞLIKLAR ---
    headers_top = [
        ("Sana", 1),
        ("Fakultet", 1),
        ("Guruh", 1),
        ("Fan", 1),
        ("O'qituvchi", 1),
        ("Pedagog darsga keldimi", 3),
        ("O'qituvchining nutq va muomala madaniyati", 4),
        ("O'tilayotgan mavzuning amaliyotga bog'langanligi", 3),
        ("Yakunlangan darsga shaxsiy qoldirgan bahosi", 4),
    ]

    col = 1
    for title, span in headers_top:
        start_row = 1
        end_row = 2 if span == 1 else 1
        start_col = col
        end_col = col + span - 1
        ws.merge_cells(start_row=start_row, start_column=start_col, end_row=end_row, end_column=end_col)
        ws.cell(row=1, column=col, value=title)
        ws.cell(row=1, column=col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.cell(row=1, column=col).font = Font(bold=True)
        col += span

    # --- ALT BAŞLIKLAR ---
    subheaders = [
        "Ha", "Yo'q", "Javobsiz",
        "A'lo", "Qoniqarli", "Qoniqarsiz", "Javobsiz",
        "Ha", "Yo'q", "Javobsiz",
        "A'lo", "Qoniqarli", "Qoniqarsiz", "Javobsiz",
    ]
    start_sub_col = 6
    for i, header in enumerate(subheaders, start=start_sub_col):
        ws.cell(row=2, column=i, value=header)
        ws.cell(row=2, column=i).alignment = Alignment(textRotation=90)

    for i in range(1, 6):
        ws.cell(row=1, column=i).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=1, column=i).font = Font(bold=True)

    # --- VERİLER ---
    qs = (
        SchedulePoint.objects.filter(schedule_id__in=schedules_id)
        .values(
            "schedule_id",
            "schedule__lesson_date",
            "schedule__group__name",
            "schedule__subject__name",
            "schedule__faculty__name",
            "schedule__employee__first_name",
            "schedule__employee__second_name",
        )
        .annotate(
            teacher_present_0=Count(Case(When(is_teacher_present="0", then=1), output_field=IntegerField())),
            teacher_present_1=Count(Case(When(is_teacher_present="1", then=1), output_field=IntegerField())),
            teacher_present_2=Count(Case(When(is_teacher_present="2", then=1), output_field=IntegerField())),
            speech_0=Count(Case(When(teacher_speech_and_culture="0", then=1), output_field=IntegerField())),
            speech_1=Count(Case(When(teacher_speech_and_culture="1", then=1), output_field=IntegerField())),
            speech_2=Count(Case(When(teacher_speech_and_culture="2", then=1), output_field=IntegerField())),
            speech_3=Count(Case(When(teacher_speech_and_culture="3", then=1), output_field=IntegerField())),
            relevance_0=Count(Case(When(topic_practical_relevance="0", then=1), output_field=IntegerField())),
            relevance_1=Count(Case(When(topic_practical_relevance="1", then=1), output_field=IntegerField())),
            relevance_2=Count(Case(When(topic_practical_relevance="2", then=1), output_field=IntegerField())),
            feedback_0=Count(Case(When(lesson_feedback="0", then=1), output_field=IntegerField())),
            feedback_1=Count(Case(When(lesson_feedback="1", then=1), output_field=IntegerField())),
            feedback_2=Count(Case(When(lesson_feedback="2", then=1), output_field=IntegerField())),
            feedback_3=Count(Case(When(lesson_feedback="3", then=1), output_field=IntegerField())),
        )
    )

    for row in qs:
        date_str = row["schedule__lesson_date"].strftime("%Y-%m-%d") if row["schedule__lesson_date"] else ""
        ws.append([
            date_str,
            row["schedule__faculty__name"],
            row["schedule__group__name"],
            row["schedule__subject__name"],
            f"{row['schedule__employee__first_name']} {row['schedule__employee__second_name']}",
            row["teacher_present_1"], row["teacher_present_2"], row["teacher_present_0"],
            row["speech_3"], row["speech_1"], row["speech_2"], row["speech_0"],
            row["relevance_1"], row["relevance_2"], row["relevance_0"],
            row["feedback_3"], row["feedback_1"], row["feedback_2"], row["feedback_0"],
        ])

    # --- STİL ---
    thin = Side(border_style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    max_row = ws.max_row
    max_col = ws.max_column

    for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            align = cell.alignment
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True, textRotation=align.textRotation
            )
            cell.border = border

    ws.row_dimensions[1].height = 74
    ws.row_dimensions[2].height = 60

    for c in range(1, 6):
        ws.column_dimensions[chr(64 + c)].width = 18
    for c in range(6, max_col + 1):
        ws.column_dimensions[chr(64 + c)].width = 6

    # --- DATA BAR ---
    databar_blue = DataBarRule(start_type="min", end_type="max", color="4472C4")
    databar_green = DataBarRule(start_type="min", end_type="max", color="70AD47")
    databar_orange = DataBarRule(start_type="min", end_type="max", color="ED7D31")

    ws.conditional_formatting.add(f"F3:F{max_row}", databar_green)
    ws.conditional_formatting.add(f"I3:I{max_row}", databar_green)
    ws.conditional_formatting.add(f"M3:M{max_row}", databar_green)
    ws.conditional_formatting.add(f"P3:P{max_row}", databar_green)

    ws.conditional_formatting.add(f"G3:G{max_row}", databar_orange)
    ws.conditional_formatting.add(f"K3:K{max_row}", databar_orange)
    ws.conditional_formatting.add(f"N3:N{max_row}", databar_orange)
    ws.conditional_formatting.add(f"R3:R{max_row}", databar_orange)

    ws.conditional_formatting.add(f"H3:H{max_row}", databar_blue)
    ws.conditional_formatting.add(f"L3:L{max_row}", databar_blue)
    ws.conditional_formatting.add(f"O3:O{max_row}", databar_blue)
    ws.conditional_formatting.add(f"S3:S{max_row}", databar_blue)

    # --- ÇIKTI ---
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'fan_boyicha_statistika_{now_str}.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



