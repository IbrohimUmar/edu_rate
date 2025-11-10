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


    @property
    def get_question_context_name(self):
        s = self.answer.schedule
        t = s.employee
        l = s.lesson_pair
        st = self.answer.student
        q = self.survey_question
        context = {
            "fan_nomi": s.subject.name,
            "fan_kodi": s.subject.code,
            "ustoz_ismi": t.first_name,
            "ustoz_familiyasi": t.second_name,
            "ustoz_fish": t.full_name,
            "semester_nomi": s.semester.name,
            "semester_kodi": s.semester.code,
            "talim_yili": s.education_year.name,
            "guruh_nomi": s.group.name,
            "guruh_kodi": s.group.code,
            "fakultet_nomi": s.faculty.name,
            "fakultet_kodi": s.faculty.code,
            "kafedra_nomi": s.department.name,
            "kafedra_kodi": s.department.code,
            "dars_sanasi": s.lesson_date.strftime("%d.%m.%Y"),
            "dars_boshlanish_vaqti": l.start_time,
            "dars_tugash_vaqti": l.end_time,
            "talaba_ismi": st.first_name,
            "talaba_familiyasi": st.second_name,
            "talaba_fish": st.full_name,
        }
        return q.name.format(**context)