from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from models.models.meta import EducationType


@login_required(login_url='login')
def survey_detail(request, id):
    education_type = get_object_or_404(EducationType, id=id)

    if request.method == 'POST':
        print(request.POST)

    return render(request, "survey/detail.html", {"education_type":education_type})
