from django.db import models
from models.models.meta import Subject, Semester, EducationYear, Group, Department, TrainingType, LessonPair, \
    EducationType, EducationForm
from models.models.schedule import Schedule
from models.models.user import User

class Survey(models.Model):
    type_choice = (
        ("1", "Schedule"),
        ("2", "Custom"),
    )
    type = models.CharField(max_length=1, choices=type_choice, default="1", null=False, blank=False)
    education_type = models.ForeignKey(
        EducationType,
        verbose_name="EducationType - Ta'lim shakli",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Survey - So'rovnoma"
        ordering = ['-created_at']



class SurveyQuestion(models.Model):
    type_choice = (
        ("1", "2-javobli"),
        ("2", "3-javobli"),
    )
    type = models.CharField(max_length=1, choices=type_choice, default="1", null=False, blank=False)
    survey = models.ForeignKey(
        Survey,
        verbose_name="O'quv reja",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "SurveyQuestion - So'rovnoma savoli"
        ordering = ['-created_at']


class SurveyAnswerOption(models.Model):
    type_choice = (
        ("1", "Pozitiv"),
        ("2", "Normal"),
        ("3", "Negative"),
    )
    type = models.CharField(max_length=1, choices=type_choice, default="1", null=False, blank=False)
    question = models.ForeignKey(
        SurveyQuestion,
        verbose_name="O'quv reja",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "SurveyAnswerOption - So'rovnoma savoli javobi"
        ordering = ['-created_at']
