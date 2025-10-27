# views.py
from rest_framework import generics

from models.models.schedule import Schedule
from .serializers import ScheduleSerializer
from api.permissions import BotChatIdPermission, BotTokenPermission
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ScheduleListView(generics.ListAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [BotChatIdPermission, BotTokenPermission]

    def get_queryset(self):
        user = self.request.user
        group = user.student.group
        now = timezone.now()
        weekday = now.weekday()  # Monday=0, Sunday=6
        if weekday == 6:  # Yakshanba
            monday = now + timedelta(days=1)  # Keyingi hafta dushanba
        else:
            monday = now - timedelta(days=weekday)  # Shu haftaning dushanbasi
        sunday = monday + timedelta(days=6)  # Haftaning yakuniy kuni
        return Schedule.objects.filter(
            group=group,
            lesson_date__date__range=[monday.date(), sunday.date()]
        )


class ScheduleDetailByIdView(APIView):
    permission_classes = [BotTokenPermission]

    def post(self, request, *args, **kwargs):
        schedule_id = request.data.get("schedule_id")
        if not schedule_id:
            return Response({"message": "Error schedule_id is required", 'status':400}, status=status.HTTP_400_BAD_REQUEST)

        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response({"message": "Error schedule not found", 'status':404}, status=status.HTTP_404_NOT_FOUND)

        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)
