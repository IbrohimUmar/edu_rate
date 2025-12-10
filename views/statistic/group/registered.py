import io

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q

from models.models.meta import Group


@login_required(login_url='login')
def statistic_group_registered(request):
    search_query = request.GET.get('search', '').strip()
    export_to_excel = request.GET.get('export') == 'excel'
    groups = Group.objects.filter(is_active=True).annotate(
        # total_students=Count('student'),
        total_students=Count('student', filter=Q(student__student_status__code=11)),
        registered_students=Count('student', filter=Q(student__user__telegram_id__isnull=False)),
        most_be_registered_count=F("total_students")-F("registered_students")
    )
    if search_query:
        groups = groups.filter(Q(name__icontains=search_query)|Q(department__name__icontains=search_query))

    is_registered = request.GET.get('is_registered', '0')
    if is_registered != '0':
        if is_registered == '1':
            groups = groups.filter(registered_students__gt=0)
        elif is_registered == '2':
            groups = groups.filter(registered_students=0)


    groups = groups.values(
        'id', 'name', 'code', 'department__name', 'total_students', 'registered_students', 'most_be_registered_count'
    )
    if export_to_excel:
        print(export_to_excel)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "KPI"

        # Sarlavha
        ws.append(['Guruh nomi', "Ro'yxatdan o'tganlarni soni", "Ro'yxatdan o'tishi kerak bo'lganlar soni"])

        for row in groups:
            ws.append([
                row['name'],
                row['registered_students'] or 0,
                row['most_be_registered_count'] or 0
            ])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Guruh bo\'yicha ro\'yxatdan o\'tmaganlar.xlsx"'
        return response
    # Pagination (20 ta sahifada)
    paginator = Paginator(groups, 30)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    queryset_count = paginator.count     # ← umumiy ma'lumotlar soni
    context = {
        'queryset': queryset,
        'queryset_count': queryset_count
    }
    return render(request, 'statistic/group/registered.html', context)
