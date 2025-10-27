import requests
import traceback
import logging
from django.conf.global_settings import DEBUG
from config.settings import ERROR_HANDLER_TELEGRAM_BOT_TOKEN, ERROR_HANDLER_TELEGRAM_CHANNEL_ID, UNIVERSITY_SHORT_NAME


def notify_error(request,error_text, status):
    message = (f"<b>URL: {request.build_absolute_uri()}</b>\n"
               f"Status : {status}\n"
               f"Method : {request.method}\n"
               f"<pre>{error_text}</pre>")
    send_message(message)



def notify_trancaction_error(message_title, error_text):
    message = (
        f"<b>Project : EduRate : {UNIVERSITY_SHORT_NAME}</b>\n"
        f"<b>Error name : {message_title}</b>\n"
               f"<pre>{error_text}</pre>")
    send_message(message)


def send_message(message):
    developer_logger = logging.getLogger('developer_logger')
    url = f"https://api.telegram.org/bot{ERROR_HANDLER_TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": ERROR_HANDLER_TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": 'HTML',
        "disable_web_page_preview": True,
        "disable_notification": False,
    }
    try:
        response = requests.post(url, data=params)
        return True
    except requests.exceptions.RequestException as e:
        error_message = traceback.format_exc()  # Traceback detaylarını al
        developer_logger.error(f"Telegram send notification error (RequestException):\n{error_message}")
        return False
    except Exception as e:
        error_message = traceback.format_exc()
        developer_logger.error(f"Telegram send notification error (All error Hata):\n{error_message}")
        return False