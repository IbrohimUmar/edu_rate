from django.db import models
from .meta import StudentStatus, EducationForm, EducationType, EducationLang, PaymentForm, StudentType, Department, \
    Specialty, Group, StudentLevel, SocialCategory
from .user import User


class StudentMeta(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shingstudents
        related_query_name='student',
    )
    hemis_id = models.IntegerField(
        verbose_name="Hemis Student ID",
        null=True,
        blank=True,
        unique=True,
    )
    student_status = models.ForeignKey(
        StudentStatus,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    education_form = models.ForeignKey(
        EducationForm,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    education_type = models.ForeignKey(
        EducationType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    payment_form = models.ForeignKey(
        PaymentForm,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    student_type = models.ForeignKey(
        StudentType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )

    level = models.ForeignKey(
        StudentLevel,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    social_category = models.ForeignKey(
        SocialCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student',  # Bu qatorni qo'shing
        related_query_name='student',
    )
    is_active = models.BooleanField(null=False, blank=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





class StudentObjection(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="student_objection_student", null=True, blank=True)
    message = models.TextField(null=True, blank=True, help_text="Habar")

    reads_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="student_objection_employee", null=True, blank=True)
    reads_at = models.DateTimeField(null=True, blank=True, default=None, help_text="Habarni o'qigan sana")

    created_at = models.DateTimeField(auto_now_add=True)