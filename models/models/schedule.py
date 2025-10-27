from django.db import models
from models.models.meta import Subject, Semester, EducationYear, Group, Department, TrainingType, LessonPair
from models.models.user import User

class Schedule(models.Model):
    hemis_id = models.IntegerField(unique=True, null=False, blank=False)
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
    def group_student_count(self):
        from .student_meta import StudentMeta
        return StudentMeta.objects.filter(group=self.group).count()

    @property
    def group_student_login_count(self):
        from .student_meta import StudentMeta
        return StudentMeta.objects.filter(group=self.group, user__telegram_id__isnull=False).count()

    @property
    def answer_send_count(self):
        from .schedule_point import SchedulePoint
        return SchedulePoint.objects.filter(schedule_id=self.id).exclude(is_teacher_present='0').count()