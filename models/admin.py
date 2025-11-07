from django.contrib import admin
from django.contrib.auth.hashers import check_password, make_password

from .models.answer import Answer
from .models.user import User
from .models.meta import Department, EducationForm, Group, EducationType, EmploymentForm
from .models.student_meta import StudentMeta
from .models.employee_meta import EmployeeMeta
from .models.schedule import Schedule

# Register your models here.
@admin.register(Department, StudentMeta, EmployeeMeta, EducationForm, EmploymentForm, EducationType, Answer)
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




# @admin.register(SchedulePoint)
# class SchedulePointAdmin(admin.ModelAdmin):
#     list_display = ['student', 'schedule', 'is_submit_notification', 'notification_planned_date', 'notification_sent_at', 'submission_deadline', 'answer_submitted_at']
#     list_editable = ('is_submit_notification', 'answer_submitted_at',)
#     list_filter = ['is_submit_notification']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'hemis_id', 'full_name', 'hemis_id_number', 'type', 'telegram_id')
    list_filter = ('type',)
    search_fields = ('full_name','hemis_id_number', 'telegram_id')
    inlines = [StudentMetaInline, EmployeeMetaInline]

    def save_model(self, request, obj, form, change):
        try:
            user_database = User.objects.get(pk=obj.pk)
        except Exception:
            user_database = None
        if user_database is None \
                or not (check_password(form.data['password'], user_database.password)
                        or user_database.password == form.data['password']):
            obj.password = make_password(obj.password)
        else:
            obj.password = user_database.password
        super().save_model(request, obj, form, change)