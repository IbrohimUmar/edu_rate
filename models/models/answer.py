from django.db import models

from models.models.survey import Survey, SurveyQuestion, SurveyAnswerOption
from models.models.user import User
from models.models.schedule import Schedule


class Answer(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="answer_student", null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="answer_employee", null=True, blank=True)

    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.SET_NULL, null=True, blank=True)

    is_submit_notification = models.BooleanField(null=False, blank=False,default=False,  help_text="Notification yuborildimi")

    notification_planned_date = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification yuborilishi rejalashtirilgan sana")
    submission_deadline = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification deadline sanasi")
    notification_sent_at  = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification yuborilgan sana")
    answer_submitted_at  = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification Javob yuborilgan sana")

    class Meta:
        verbose_name = "Answer - Javob"
        verbose_name_plural = "Answer - Javob"


class AnswerDetail(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    survey_question = models.ForeignKey(SurveyQuestion, on_delete=models.SET_NULL, null=True, blank=True)
    survey_answer_option = models.ForeignKey(SurveyAnswerOption, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "AnswerDetail - Savol javobi"
        verbose_name_plural = "AnswerDetail - Savol javoblari"