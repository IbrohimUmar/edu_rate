import io, datetime
from threading import Thread

from django.contrib import messages
from django.shortcuts import render, redirect

from django.core.paginator import Paginator
from django.utils.timezone import now

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from models.models.schedule import Schedule
from django.db.models import Count, Q

from models.models.survey import Survey
from services.export_file.schedule.format1.manager import export_file_schedule_format1_manager



@login_required(login_url='login')
def survey_schedule_list(request, id):
    survey = get_object_or_404(Survey, id=id)
    search_query = request.GET.get('search', '').strip()
    export_to_excel = request.GET.get('export') == 'excel'
    selected_date = None
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()

    # schedules = Schedule.objects.filter(employee=teacher,
    #                                     lesson_date__date=selected_date
    #                                     ).order_by('lesson_date')
    schedules = Schedule.objects.filter(survey=survey).order_by('-lesson_date')

    if date_str:
        schedules = schedules.filter(lesson_date__date=selected_date)

    schedules = (
        schedules
        .annotate(
            group_student_count_qs=Count("group__student", distinct=True),
            answer_send_count_qs=Count(
                "answer",
                filter=Q(answer__answer_submitted_at__isnull=False),  # sadece cevap gönderenler
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

    from_date = request.GET.get('from_date')  # '2023-10-01' formatında geldiğini varsayıyorum
    to_date = request.GET.get('to_date')
    if from_date:
        schedules = schedules.filter(lesson_date__gte=from_date)
    if to_date:
        schedules = schedules.filter(lesson_date__date__lte=to_date)

    if search_query:
        schedules = schedules.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__second_name__icontains=search_query) |
            Q(employee__third_name__icontains=search_query)
        )

    if export_to_excel:
        # data = export_file_schedule_format1_data_format(schedules, survey)
        # return export_file_schedule_format1_export_excel(data, survey)

        thread = Thread(target=export_file_schedule_format1_manager, args=(schedules, survey, request.user))
        thread.start()
        messages.success(request, "Fayl eksport qilinmoqda..")
        return redirect('survey_schedule_list', id)

    page = request.GET.get('page', 1)
    paginator = Paginator(schedules, 50)  # sahifada 25 ta qator
    queryset = paginator.get_page(page)  # ← SENING HTML'DAGI NOM
    queryset_count = paginator.count     # ← umumiy ma'lumotlar soni
    context = {
        'queryset': queryset,
        'queryset_count': queryset_count,
        'selected_date': selected_date
    }
    return render(request, "survey/schedule/list.html", context)
