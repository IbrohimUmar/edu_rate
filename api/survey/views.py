# views.py
from rest_framework import generics

from models.models.answer import Answer
from models.models.schedule import Schedule
from .serializers import ScheduleSerializer, AnswerListSerializer, AnswerSubmitSerializer
from api.permissions import BotChatIdPermission, BotTokenPermission
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

class AnswerSubmitView(APIView):
    permission_classes = [BotChatIdPermission, BotTokenPermission]

    def post(self, request):
        serializer = AnswerSubmitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            answer = serializer.validated_data['answer']
            serializer.update(answer, serializer.validated_data)
            return Response({'status':200, "detail": [], 'message':'Baho tasdiqlandi'}, status=200)
        return Response({'status':400, 'details':serializer.errors, 'message':'error'}, status=400)


class ActiveAnswerListView(generics.ListAPIView):
    serializer_class = AnswerListSerializer
    permission_classes = [BotChatIdPermission, BotTokenPermission]

    def get_queryset(self):
        now = timezone.now()
        survey_id = self.request.query_params.get("survey_id", '0')  # <-- GET parametresi

        queryset = (
            Answer.objects.filter(is_submit_notification=True)
            .filter(submission_deadline__gt=now, student_id=self.request.user.id)
            .select_related("schedule", "survey", "employee", "student")
            .prefetch_related("answerdetail_set")
        )
        print(survey_id, self.request.query_params)
        if survey_id is not None and len(survey_id) > 0 and survey_id not in [0, '0']:
            queryset = queryset.filter(id=survey_id)

        return queryset


    # def get_queryset(self):
    #     now = timezone.now()
    #     return (
    #         Answer.objects.filter(is_submit_notification=True)
    #         .filter(submission_deadline__gt=now,
    #                 student_id=self.request.user.id)
    #         .select_related("schedule", "survey", "employee", "student")
    #         .prefetch_related("answerdetail_set")
    #     )







        # print(self.request.user.id)
        # an = Answer.objects.filter(student=self.request.user)
        # print(an)
        # return (
        #     Answer.objects
        #     .filter(submission_deadline__gt=now,
        #             student_id=self.request.user.id)
        #     .select_related("schedule", "survey", "employee", "student")
        #     .prefetch_related("answerdetail_set")
        # )