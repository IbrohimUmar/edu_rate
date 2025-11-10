# serializers.py
from datetime import datetime

from rest_framework import serializers

from django.utils import timezone
from rest_framework import serializers

from models.models.answer import AnswerDetail, Answer
from models.models.meta import Department, Subject, Group
from models.models.schedule import Schedule
from models.models.student_meta import StudentObjection
from models.models.survey import Survey, SurveyQuestion, SurveyAnswerOption
from models.models.user import User




class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "full_name"]



class ScheduleSerializer(serializers.ModelSerializer):
    subject_data = serializers.SerializerMethodField()


    class Meta:
        model = Schedule
        fields = [
            "id",
            "hemis_id",
            "subject_data",
            "lesson_date",
        ]

    def get_subject_data(self, obj):
        return {
            "id":obj.subject.id,
            "code":obj.subject.code,
                "name":obj.subject.name}



class SurveyAnswerOptionForQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAnswerOption
        fields = ["id", "name", "type"]



class SurveyQuestionSerializer(serializers.ModelSerializer):
    survey_answer_option = SurveyAnswerOptionForQuestionSerializer(
        many=True, read_only=True, source="surveyansweroption_set"
    )
    # survey_answer_option = SurveyAnswerOptionForQuestionSerializer()
    class Meta:
        model = SurveyQuestion
        fields = ["id", "type", "survey_answer_option"]



class SurveyAnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAnswerOption
        fields = ["id", "name", "type"]


class AnswerDetailSerializer(serializers.ModelSerializer):
    survey_question = SurveyQuestionSerializer()
    question_name = serializers.SerializerMethodField()

    class Meta:
        model = AnswerDetail
        fields = ["id", "survey_question", 'question_name']


    def get_question_name(self, obj):
        return obj.get_question_context_name

class AnswerListSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer()
    questions = serializers.SerializerMethodField()
    teacher_data = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            "id",
            "student",
            "teacher_data",
            "schedule",
            "submission_deadline",
            "questions",
        ]

    def get_teacher_data(self, obj):
        return {'id': obj.employee.id,
                'full_name': obj.employee.full_name,
                }

    def get_questions(self, obj):
        details = AnswerDetail.objects.filter(answer=obj).order_by("id")
        return AnswerDetailSerializer(details, many=True).data




class QuestionAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_option_id = serializers.IntegerField()


class AnswerSubmitSerializer(serializers.Serializer):
    answer_id = serializers.IntegerField(required=True)
    questions = QuestionAnswerInputSerializer(many=True)

    def validate(self, data):
        answer_id = data["answer_id"]
        questions = data["questions"]
        request = self.context.get('request')
        user = request.user

        # 1️⃣ Answer var mı kontrol et
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            raise serializers.ValidationError("Bunday answer topilmadi.")

        if answer.student.id != user.id:
            raise serializers.ValidationError("Bu answer_id sizga tegishli emas")

        if answer.answer_submitted_at is not None:
            raise serializers.ValidationError("Bu dars uchun baho qo'yib bo'lingan.")

        if answer.submission_deadline and answer.submission_deadline < timezone.now():
            raise serializers.ValidationError("Bu dars uchun javob berish muddati tugagan.")

        # 2️⃣ Her bir question’u tek tek kontrol et
        for q in questions:
            question_id = q["question_id"]
            answer_option_id = q["answer_option_id"]

            # SurveyQuestion bormi?
            if not AnswerDetail.objects.filter(id=question_id).exists():
                raise serializers.ValidationError(
                    f"Question ID {question_id} topilmadi."
                )
            # SurveyAnswerOption bormi?
            if not SurveyAnswerOption.objects.filter(id=answer_option_id).exists():
                raise serializers.ValidationError(
                    f"Answer option ID {answer_option_id} topilmadi."
                )

            # AnswerDetail'da bu soru zaten cevaplanmişmi?
            if AnswerDetail.objects.filter(answer=answer, survey_question_id=question_id).exists():
                raise serializers.ValidationError(
                    f"Savol {question_id} allaqachon javob berilgan."
                )
        data['answer'] = answer
        return data

    def update(self, instance, validated_data):
        """Mavjud javoblarni yangilaydi yoki yangisini yaratadi"""
        from django.utils import timezone

        questions = validated_data["questions"]

        for q in questions:
            question_id = q["question_id"]
            answer_option_id = q["answer_option_id"]

            # Agar mavjud bo‘lsa, yangilaymiz
            answer_detail, created = AnswerDetail.objects.update_or_create(
                answer=instance,
                id=question_id,
                defaults={"survey_answer_option_id": answer_option_id}
            )
        # Answerning umumiy maydonlarini ham yangilaymiz
        instance.answer_submitted_at = timezone.now()
        instance.save(update_fields=["answer_submitted_at"])

        return instance