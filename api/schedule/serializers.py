# serializers.py
from datetime import datetime

from rest_framework import serializers

from django.utils import timezone
from rest_framework import serializers

from models.models.meta import Department, Subject, Group
from models.models.schedule import Schedule
from models.models.student_meta import StudentObjection
from models.models.user import User


class DepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'hemis_id', 'code']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'hemis_id', 'code']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'hemis_id', 'code']


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'second_name', 'third_name', 'full_name', 'hemis_id_number']


class StudentObjectionSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = StudentObjection
        fields = ['message']

class ScheduleSerializer(serializers.ModelSerializer):
    faculty = DepartmentListSerializer()
    department = DepartmentListSerializer()
    subject = SubjectSerializer()
    group = GroupSerializer()
    employee = CustomUserSerializer()

    class Meta:
        model = Schedule
        fields = '__all__'
        depth = 1

