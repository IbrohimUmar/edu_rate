from django.contrib import admin

from .models.answer import AnswerDetail, Answer
from .models.survey import SurveyAnswerOption, SurveyQuestion, Survey
from .models.user import User
from .models.meta import Department, EducationForm, Group
from .models.student_meta import StudentMeta
from .models.employee_meta import EmployeeMeta
from .models.schedule import Schedule

# Register your models here.
@admin.register(Department, StudentMeta, EmployeeMeta)
class DefaultAdmin(admin.ModelAdmin):
    pass


class StudentMetaInline(admin.TabularInline):
    model = StudentMeta
    extra = 0

class EmployeeMetaInline(admin.TabularInline):
    model = EmployeeMeta
    extra = 0

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['hemis_id', 'group','subject', 'lesson_pair', 'lesson_date', 'week', 'employee',
                    'group_student_count', 'group_student_login_count']
    list_filter = ['lesson_pair', 'lesson_date']
    search_fields = ['hemis_id']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'hemis_id', 'full_name', 'hemis_id_number', 'type', 'telegram_id')
    list_filter = ('type',)
    search_fields = ('full_name','hemis_id_number', 'telegram_id')
    inlines = [StudentMetaInline, EmployeeMetaInline]




# ---------------------------
# Inline konfiguratsiyalar
# ---------------------------

class SurveyAnswerOptionInline(admin.TabularInline):
    model = SurveyAnswerOption
    extra = 0
    fields = ('name', 'type')
    ordering = ['id']


class SurveyQuestionInline(admin.TabularInline):
    model = SurveyQuestion
    extra = 0
    fields = ('name', 'type')
    ordering = ['id']


class AnswerDetailInline(admin.TabularInline):
    model = AnswerDetail
    extra = 0
    fields = ('survey_question', 'survey_answer_option')
    autocomplete_fields = ['survey_question', 'survey_answer_option']
    ordering = ['id']


# ---------------------------
# Survey Admin
# ---------------------------

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'education_form', 'type', 'created_at')
    list_filter = ('education_form', 'type')
    search_fields = ('name',)
    inlines = [SurveyQuestionInline]
    ordering = ['-created_at']


# ---------------------------
# SurveyQuestion Admin
# ---------------------------

@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)
    inlines = [SurveyAnswerOptionInline]
    ordering = ['-created_at']


# ---------------------------
# SurveyAnswerOption Admin
# ---------------------------

@admin.register(SurveyAnswerOption)
class SurveyAnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'question')
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ['-created_at']



# ---------------------------
# Answer Admin
# ---------------------------

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'employee',
        'schedule',
        'survey',
        'is_submit_notification',
        'notification_planned_date',
        'notification_sent_at',
        'answer_submitted_at'
    )
    list_filter = (
        'is_submit_notification',
        'survey',
        'schedule',
    )
    search_fields = ('student__first_name', 'student__last_name', 'survey__name')
    readonly_fields = (
        'notification_sent_at',
        'answer_submitted_at',
    )
    inlines = [AnswerDetailInline]
    ordering = ['-id']


# ---------------------------
# AnswerDetail Admin
# ---------------------------

@admin.register(AnswerDetail)
class AnswerDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'survey_question', 'survey_answer_option')
    list_filter = ('survey_question',)
    search_fields = ('answer__student__first_name', 'survey_question__name')
    ordering = ['-id']