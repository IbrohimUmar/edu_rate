from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from models.models.user import User

@login_required(login_url='login')
def setting_user_list(request):
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)
    users_qs = User.objects.filter(type='1').order_by('-id')

    if search_query:
        users_qs = users_qs.filter(full_name__icontains=search_query)

    paginator = Paginator(users_qs, 50)  # sahifada 25 ta qator
    queryset = paginator.get_page(page)  # ← SENING HTML'DAGI NOM
    queryset_count = paginator.count     # ← umumiy ma'lumotlar soni
    context = {
        'queryset': queryset,
        'queryset_count': queryset_count,
    }
    return render(request, "setting/user/list.html", context)

