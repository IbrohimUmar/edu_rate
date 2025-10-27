from rest_framework import serializers

from models.models.student_meta import StudentObjection


class StudentObjectionSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = StudentObjection
        fields = ['message']
