from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from models.models.schedule_point import SchedulePoint


class SchedulePointUpdateSerializer(serializers.Serializer):
    schedule_point_id = serializers.IntegerField(required=True)
    answer1 = serializers.ChoiceField(required=True, choices=[1, 2])
    answer2 = serializers.ChoiceField(required=True, choices=[1, 2, 3])
    answer3 = serializers.ChoiceField(required=True, choices=[1, 2])
    answer4 = serializers.ChoiceField(required=True, choices=[1, 2, 3])



    def validate(self, data):
        request = self.context.get('request')
        student = request.user.student

        try:
            schedule_point = SchedulePoint.objects.get(id=data['schedule_point_id'], student=request.user)
            # schedule_point = SchedulePoint.objects.get(id=data['schedule_point_id'])
            # schedule_point = SchedulePoint.objects.first()

            if schedule_point.answer_submitted_at is not None:
                raise serializers.ValidationError("Bu dars uchun baho qo'yib bo'lingan.")

            if schedule_point.submission_deadline and schedule_point.submission_deadline < timezone.now():
                raise serializers.ValidationError("Bu dars uchun javob berish muddati tugagan.")

        except SchedulePoint.DoesNotExist:
            raise serializers.ValidationError("Dars mavjud emas.")

        data['schedule_point'] = schedule_point
        return data

    def update(self, instance, validated_data):
        # instance.point = validated_data['point']
        if int(validated_data['answer1']) == 1:
            instance.is_teacher_present = validated_data['answer1']
            instance.teacher_speech_and_culture = validated_data['answer2']
            instance.topic_practical_relevance = validated_data['answer3']
            instance.lesson_feedback = validated_data['answer4']
            instance.answer_submitted_at = datetime.now()
        else:
            instance.is_teacher_present = '2'
            instance.answer_submitted_at = datetime.now()
        instance.save()
        return instance

    def create(self, validated_data):
        # Create kullanmayacağız, update-only serializer.
        raise NotImplementedError("Use only for update")
