from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from models.models.answer import Answer, AnswerDetail
from models.models.schedule import Schedule
# from models.models.schedule_point import SchedulePoint
from models.models.student_meta import StudentMeta
from models.models.survey import SurveyQuestion


@login_required(login_url='login')
def schedule_details(request, id):
    schedule = get_object_or_404(Schedule, id=id)

    # Tüm cevapları alıyoruz
    answers = Answer.objects.filter(schedule=schedule).prefetch_related(
        'answerdetail_set',
        'answerdetail_set__survey_answer_option',
        'answerdetail_set__survey_question'
    )

    survey_questions = SurveyQuestion.objects.filter(survey=schedule.survey).order_by('order_position')

    # Henüz cevap vermemiş öğrenciler
    unregister_students = StudentMeta.objects.filter(group=schedule.group).exclude(
        user_id__in=list(answers.values_list('student_id', flat=True))
    )

    return render(request, "schedule/details.html", {
        'schedule': schedule,
        'answers': answers,
        'survey_questions': survey_questions,
        'unregister_students': unregister_students,
        'employee': schedule.employee,
        'answer_map': schedule.get_answers_map
    })

@login_required(login_url='login')
def schedule_details_old(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    answers = Answer.objects.filter(schedule=schedule)



    survey_questions = SurveyQuestion.objects.filter(survey=schedule.survey).order_by('order_position')


    unregister_students = StudentMeta.objects.filter(group=schedule.group).exclude(user_id__in=list(answers.values_list('student_id', flat=True)))
    return render(request, "schedule/details.html", {
        'schedule': schedule,
        'answers': answers,
        'survey_questions': survey_questions,
        'unregister_students': unregister_students,
        'employee': schedule.employee})



