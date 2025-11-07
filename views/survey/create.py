from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import lower

from models.models.meta import EducationType
import json

from models.models.survey import Survey, SurveyQuestion, SurveyAnswerOption
from services.handle_exception import handle_exception


@login_required(login_url='login')
def survey_create(request, id):
    education_type = get_object_or_404(EducationType, id=id)

    survey = Survey.objects.filter(education_type=education_type, is_active=True).first()
    if survey:
        messages.error(request, f"Kechirasiz aktiv bo'lgan {lower(education_type.name)} uchun yaratilgan so'rovnoma mavjud")
        return redirect("survey_list")

    if request.method == 'POST':
        try:
            with transaction.atomic():
                r = request.POST
                question_data = json.loads(r['question'])

                survey = Survey.objects.create(
                    type='1',
                    education_type=education_type,
                    name=f"{education_type.name} talabasi darslari uchun so'rovnoma"
                )

                for q in question_data:
                    survey_question = SurveyQuestion.objects.create(
                        type=q.get('answer_type', '1'),
                        survey=survey,
                        name=q.get('text')
                    )
                    for answer in q.get('answers', []):
                        name = answer.get('text')
                        type_ = answer.get('type', '1')
                        SurveyAnswerOption.objects.update_or_create(
                            question=survey_question,
                            name=name,
                            type=type_
                        )

                messages.success(request, "Qo'shildi")
                return redirect("survey_list")
        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Xato yuzaga keldi {e}")
            return redirect('survey_create', id)

    return render(request, "survey/create.html", {
        "education_type":education_type})


