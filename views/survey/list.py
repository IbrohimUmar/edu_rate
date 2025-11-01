from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models.models.meta import EducationType


@login_required(login_url='login')
def survey_list(request):
    education_type = EducationType.objects.all()
    return render(request, "survey/list.html", {"education_type":education_type})
