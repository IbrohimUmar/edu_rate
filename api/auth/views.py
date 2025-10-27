from rest_framework.decorators import permission_classes
from api.permissions import BotTokenPermission, BotChatIdPermission
from rest_framework.views import APIView
from rest_framework.response import Response

from models.models.user import User
from models.models.student_meta import StudentMeta
from services.schedule.schedule_point import create_schedule_point_by_student


class ActivationApiViews(APIView):
    permission_classes = [BotTokenPermission]

    def post(self, request):
        hemis_id_number = request.POST.get('hemis_id_number')
        chat_id = request.POST.get('chat_id')

        if not hemis_id_number or not chat_id:
            return Response({"message": "Ma'lumotlarda kamchilik bor", "status": 404}, status=404)

        old_auth_model = User.objects.filter(telegram_id=chat_id)
        if old_auth_model:
            old_auth_model.update(telegram_id=None)

        auth_model = User.objects.filter(hemis_id_number=hemis_id_number, telegram_id=chat_id).exists()
        if auth_model:
            return Response({"message": "Foydalanuvchi aktiv xolatda", "status": 200}, status=200)

        custom_user = User.objects.filter(hemis_id_number=hemis_id_number).first()
        if not custom_user:
            return Response({"message": "Bunday hemis id dagi foydalanuvchi mavjud emas", "status": 404}, status=404)

        student_meta = StudentMeta.objects.filter(user=custom_user).first()
        if not student_meta:
            return Response({"message": "Bunday student meta datasi mavjud emas", "status": 404}, status=404)


        User.objects.filter(id=custom_user.id).update(telegram_id=chat_id)
        create_schedule_point_by_student(custom_user, student_meta)
        return Response({"message": "Foydalanuvchi aktivlashtirildi", "status": 200}, status=200)





class CheckActivationApiViews(APIView):
    permission_classes = [BotTokenPermission]

    def post(self, request):
        chat_id = request.POST.get('chat_id')

        if not chat_id:
            return Response({"message": "char_id mavjud eams", "status": 404}, status=404)

        auth_model = User.objects.filter(telegram_id=chat_id).first()
        if auth_model:
            user = auth_model
            return Response({"message": "Foydalanuvchi aktiv xolatda",
                                "data":{
                                    "first_name": user.first_name,
                                    "second_name": user.second_name,
                                    "third_name": user.third_name,
                                    "full_name": user.full_name,
                                }, "status": 200}, status=200)
        return Response({"message": "Aktivlashtirilmagan", "status": 400}, status=400)


