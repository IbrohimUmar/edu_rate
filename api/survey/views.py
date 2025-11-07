# views.py
from rest_framework import generics

from models.models.answer import Answer
from models.models.schedule import Schedule
from .serializers import ScheduleSerializer, AnswerListSerializer, AnswerSubmitSerializer
from api.permissions import BotChatIdPermission, BotTokenPermission
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class AnswerSubmitView(APIView):
    permission_classes = [BotChatIdPermission, BotTokenPermission]

    # def post(self, request):
    #     serializer = AnswerSubmitSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response({"status":200, "message": "Javoblar muvaffaqiyatli saqlandi ✅"}, status=status.HTTP_201_CREATED)


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
        # return (
        #     Answer.objects.filter(is_submit_notification=False)
        #     .filter(submission_deadline__gt=now,
        #             student_id=self.request.user.id)
        #     .select_related("schedule", "survey", "employee", "student")
        #     .prefetch_related("answerdetail_set")
        # )
        return (
            Answer.objects.filter(is_submit_notification=False)
            .filter(submission_deadline__gt=now)
            # .filter(student_id=self.request.user.id)
            .select_related("schedule", "survey", "employee", "student")
            .prefetch_related("answerdetail_set")
        )[:100]