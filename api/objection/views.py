from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from models.models.student_meta import StudentObjection
from .serializers import StudentObjectionSerializer
from ..permissions import BotTokenPermission, BotChatIdPermission


class StudentObjectionAPIView(APIView):
    permission_classes = [BotChatIdPermission, BotTokenPermission]

    def post(self, request):
        serializer = StudentObjectionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            StudentObjection.objects.create(student=request.user, message=serializer.data['message'])
            return Response({'status':200, "detail": [], 'message':'Xabar qabul qilindi'}, status=200)
        return Response({'status':400, 'details':serializer.errors, 'message':'error'}, status=400)
