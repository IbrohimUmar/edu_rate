from django.db import models
from models.models.user import User
from models.models.schedule import Schedule


class SchedulePoint(models.Model):
    POINT_LEVEL_CHOICES = [
        ("0", "Baholanmagan"),
        ("1", "Qoniqarli"),
        ("2", "Qoniqarsiz"),
        ("3", "A'lo")
    ]
    BOOLEAN_CHOICES = [
        ("0", "Belgilanmagan"),
        ("1", "Ha"),
        ("2", "Yo'q")
    ]
    is_teacher_present = models.CharField(
        max_length=2,
        choices=BOOLEAN_CHOICES,
        default="0",
        verbose_name="Pedagog darsga keldimi",
        null=True,
        blank=True
    )
    teacher_speech_and_culture = models.CharField(
        max_length=2,
        choices=POINT_LEVEL_CHOICES,
        default="0",
        verbose_name="O'qituvchining nutq va muomala madaniyatini, kiyinishi va o'zini tutish etikasini qanday baxolaysiz",
        null=True,
        blank=True
    )
    topic_practical_relevance = models.CharField(
        max_length=2,
        choices=BOOLEAN_CHOICES,
        default="0",
        verbose_name="O'tilayotgan mavzuning amaliyotga bog'langanligi",
        null=True,
        blank=True
    )
    lesson_feedback = models.CharField(
        max_length=2,
        choices=POINT_LEVEL_CHOICES,
        default="0",
        verbose_name="Yakunlangan darsga shaxsiy qoldirgan bahosi",
        null=True,
        blank=True
    )
    student = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="schedule_point_student", null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="schedule_point_employee", null=True, blank=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)

    is_submit_notification = models.BooleanField(null=False, blank=False,default=False,  help_text="Notification yuborildimi")

    notification_planned_date = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification yuborilishi rejalashtirilgan sana")
    submission_deadline = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification deadline sanasi")
    notification_sent_at  = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification yuborilgan sana")
    answer_submitted_at  = models.DateTimeField(null=True, blank=True, default=None, help_text="Notification Javob yuborilgan sana")
