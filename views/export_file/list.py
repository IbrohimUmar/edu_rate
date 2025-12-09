from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from models.models.user import User
from models.models.export_file import ExportFile

@login_required(login_url='login')
def export_file_list(request):
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)
    export_file_qs = ExportFile.objects.filter(user=request.user).order_by('-id')
    if search_query:
        export_file_qs = export_file_qs.filter(name__icontains=search_query)

    is_refresh_page = False
    if export_file_qs.filter(status='processing').count() > 0:
        is_refresh_page = True
    if request.method == 'POST':
        print(request.POST)
        file = ExportFile.objects.filter(user=request.user, id=request.POST.get('id'))
        if file.exists():
            file.delete()
            messages.success(request, "Ma'lumotlar o'chirildi")
            return redirect("export_file_list")
        messages.success(request, "Bunday fayl topilmadi")
        return redirect("export_file_list")

    paginator = Paginator(export_file_qs, 50)  # sahifada 25 ta qator
    queryset = paginator.get_page(page)  # ← SENING HTML'DAGI NOM
    queryset_count = paginator.count     # ← umumiy ma'lumotlar soni
    context = {
        'queryset': queryset,
        'queryset_count': queryset_count,
        'is_refresh_page': is_refresh_page
    }
    return render(request, "export_file/list.html", context)
