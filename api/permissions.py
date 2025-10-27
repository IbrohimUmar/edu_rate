from rest_framework import permissions
from models.models.user import User
from rest_framework.exceptions import PermissionDenied
from pathlib import Path
from config.settings import TG_BOT_TOKEN, API_TOKEN


class BotTokenPermission(permissions.BasePermission):
    details = 'Siz tokenini hato kiritdingiz'
    def has_permission(self, request, view):
        if request.headers.get('API_TOKEN') == str(API_TOKEN):
            return True
        else:
            return False


from rest_framework.exceptions import APIException


class CustomPermissionDenied(APIException):
    status_code = 401  # Veya ihtiyacınıza göre bir durum kodu belirleyin
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        self.detail = {
            'detail': detail if detail is not None else self.default_detail,
            'status': self.status_code,
        }


class BotChatIdPermission(permissions.BasePermission):
    message = "Chat id not'g'ri"
    def has_permission(self, request, view):
        chat_id = request.headers.get('ChatId')
        if chat_id is not None:
            user = User.objects.filter(telegram_id=str(chat_id)).first()
            if not user:
                raise CustomPermissionDenied(detail="Chat id not'g'ri")

            request.user = user
            return True
        raise CustomPermissionDenied(detail="Chat id hederda yo'q")

