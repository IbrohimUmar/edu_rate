import datetime
import random

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from django.shortcuts import render
from django.utils import timezone

from models.models.answer import Answer, AnswerDetail
from models.models.schedule import Schedule
# from models.models.schedule_point import SchedulePoint
from models.models.student_meta import StudentMeta
from models.models.survey import SurveyAnswerOption, SurveyQuestion
from models.models.user import User
from services.schedule.schedule_point import calculate_deadline, calculate_lesson_end_time


@login_required(login_url='login')
def home(request):
    user_statistic = User.objects.filter(type='3').aggregate(
        total_student_count=Count("id"),
        total_registered_count=Count("id", Q(telegram_id__isnull=False)),
    )

    schedule_point = Answer.objects.aggregate(
        total_answers_count=Count("id", filter=Q(answer_submitted_at__isnull=False)),
        total_not_answered_count=Count("id", filter=Q(answer_submitted_at=None, is_submit_notification=True)),
        total_send_notify_count=Count("id", filter=Q(is_submit_notification=True)),
        # total_not_answered_count=F("total_answers_count")-F("total_send_notify_count"),
    )
    chart_data = []
    questions = SurveyQuestion.objects.filter(survey__is_active=True)

    for question in questions:
        # survey_answer_option = SurveyAnswerOption.objects.filter(question=question)
        answer_details = AnswerDetail.objects.filter(survey_question=question, answer__answer_submitted_at__isnull=False)

        chart_data.append({
            "question": question.name,
            "question_edu_type": question.survey.education_type,
            "positive": answer_details.filter(survey_answer_option__type='1').count(),
            "normal": answer_details.filter(survey_answer_option__type='2').count(),
            "negative": answer_details.filter(survey_answer_option__type='3').count(),
        })
    return render(request, 'home.html', {
        "schedule_point":schedule_point,
        "chart_data":chart_data,
        "user_statistic":user_statistic})



def random_generate_answer():
    answers = Answer.objects.filter(answer_submitted_at__isnull=True)
    print(answers.count())
    t = answers.count()
    for answer in answers:
        answer.is_submit_notification=True
        answer.notification_sent_at = timezone.now()
        answer.answer_submitted_at = timezone.now()
        answer.save()
        t-=1
        details = AnswerDetail.objects.filter(answer_id=answer.id)
        for detail in details:
            survey_option = SurveyAnswerOption.objects.filter(question=detail.survey_question).order_by("?").first()
            detail.survey_answer_option = survey_option
            detail.save()

        print(answer, 'ok', t)


