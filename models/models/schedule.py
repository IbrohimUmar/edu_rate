from django.db import models

from models.models.meta import Subject, Semester, EducationYear, Group, Department, TrainingType, LessonPair, Auditorium
from models.models.survey import Survey
from models.models.user import User

class Schedule(models.Model):
    hemis_id = models.IntegerField(unique=True, null=False, blank=False)
    survey = models.ForeignKey(
        Survey,
        verbose_name="Survey",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subject = models.ForeignKey(
        Subject,
        verbose_name="Fan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    semester = models.ForeignKey(
        Semester,
        verbose_name="Simester",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    education_year = models.ForeignKey(
        EducationYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    faculty = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_faculty"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_department"
    )
    training_type = models.ForeignKey(
        TrainingType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    lesson_pair = models.ForeignKey(
        LessonPair,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    auditorium = models.ForeignKey(
        Auditorium,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    week_start_time = models.DateTimeField()
    week_end_time = models.DateTimeField()
    lesson_date = models.DateTimeField()
    week = models.IntegerField(null=False, blank=False)

    is_create_schedule_point = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Schedule - Dars jadvali"
        ordering = ['-created_at']


    @property
    def get_active_survey(self):
        from models.models.student_meta import StudentMeta
        active_student = (
            StudentMeta.objects
            .filter(group=self.group)
            .only("education_type")  # sadece gereken alanı al
            .first()
        )
        if not active_student:
            return None

        return (
            Survey.objects
            .filter(education_type=active_student.education_type, is_active=True)
            .first()
        )

    @property
    def group_student_count(self):
        from .student_meta import StudentMeta
        return StudentMeta.objects.filter(group=self.group).count()

    @property
    def group_student_login_count(self):
        from .student_meta import StudentMeta
        return StudentMeta.objects.filter(group=self.group, user__telegram_id__isnull=False).count()

    @property
    def answer_send_count(self):
        from .answer import Answer
        return Answer.objects.filter(schedule_id=self.id).exclude(is_teacher_present='0').count()

    @property
    def get_answers(self):
        from .answer import Answer
        return Answer.objects.filter(schedule_id=self.id)

    @property
    def get_answers_map(self):
        answers = self.get_answers.prefetch_related(
            'answerdetail_set',
            'answerdetail_set__survey_answer_option',
            'answerdetail_set__survey_question'
        )
        answer_map = {}
        for answer in answers:
            detail_map = {}
            for detail in answer.answerdetail_set.all():  # ❗ Yeni sorgu çalıştırmaz
                if detail.survey_question_id and detail.survey_answer_option:
                    detail_map[detail.survey_question_id] = detail

            answer_map[answer.student_id] = detail_map
        return answer_map