from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from models.models.meta import EducationType
import json

from models.models.survey import Survey, SurveyQuestion, SurveyAnswerOption
from services.handle_exception import handle_exception


@login_required(login_url='login')
def survey_detail(request, id):
    survey = get_object_or_404(Survey, id=id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                r = request.POST
                question_data = json.loads(r['question'])

                is_active = {'1':True, '0':False}.get(r.get('is_active', '0'), '0')
                if survey.alternative_active_survey_exists is False:
                    survey.is_active = is_active
                    survey.save()

                for q in question_data:
                    q_id = q.get('id')
                    survey_question, q_created = SurveyQuestion.objects.update_or_create(
                        id=q_id,
                        survey=survey,
                        defaults={
                            'name': q.get('text'),
                        }
                    )
                    for answer in q.get('answers', []):
                        id = answer.get('id')
                        name = answer.get('text')
                        type_ = answer.get('type', '1')
                        SurveyAnswerOption.objects.update_or_create(
                            id=id,
                            question=survey_question,
                            defaults={
                                'name': name,
                                'type': type_
                                      },
                        )

                messages.success(request, "Ma'lumotlar o'zgartirildi")
                return redirect('survey_detail', survey.id)
        except Exception as e:
            handle_exception(e)
            messages.error(request, f"Xato yuzaga keldi {e}")
            return redirect('survey_detail', survey.id)

    example_question = []
    if survey:
        questions = survey.surveyquestion_set.prefetch_related('surveyansweroption_set').all().order_by('id')

        for q in questions:
            example_question.append({
                'id': q.id,
                'text': q.name,
                'answer_type': q.type,
                'answers': [
                    {
                        'id': a.id,
                        'text': a.name,
                        'type': a.type
                    }
                    for a in q.surveyansweroption_set.all()
                ]
            })
    return render(request, "survey/detail.html", {
        "example_question":example_question,
        "survey":survey,
    })


