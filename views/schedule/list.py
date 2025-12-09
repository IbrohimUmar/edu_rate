import io, datetime
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models.models.schedule import Schedule
from django.db.models import Count, Q

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
    if search_query:
        schedules = schedules.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__second_name__icontains=search_query) |
            Q(employee__third_name__icontains=search_query)
        )

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



