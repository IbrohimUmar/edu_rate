from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SchedulePointUpdateSerializer
from ..permissions import BotChatIdPermission, BotTokenPermission


class SchedulePointUpdateAPIView(APIView):
    permission_classes = [BotChatIdPermission, BotTokenPermission]

    def post(self, request):
        serializer = SchedulePointUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            schedule_point = serializer.validated_data['schedule_point']
            serializer.update(schedule_point, serializer.validated_data)
            return Response({'status':200, "detail": [], 'message':'Baho tasdiqlandi'}, status=200)
        return Response({'status':400, 'details':serializer.errors, 'message':'error'}, status=400)
