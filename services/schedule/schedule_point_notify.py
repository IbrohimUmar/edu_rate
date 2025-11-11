import aiohttp
import asyncio
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.core.cache import cache

from models.models.answer import Answer, AnswerDetail
from models.models.survey import SurveyAnswerOption
from models.models.user import User
from services.handle_exception import handle_exception

BOT_TOKEN = settings.TG_BOT_TOKEN  # Ayarlara bot token ekleyin


async def send_telegram_notification(tg_chat_id: str, message: str, inline_keyboards: list) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": tg_chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [inline_keyboards]
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                return data.get("ok", False)
        except Exception as e:
            handle_exception(e)
            return False


from django.utils import timezone
from asgiref.sync import async_to_sync
import time
'''
O'quvchilar darsni baholashi uchun notification yuborish func
dars boshlanganiga 40 daqiqa bo'lganidan keyin bu func talaba botni aktivlashtirgan profiliga
darsni baholashi uchun notification yuboradi
har 2 daqiqada ishlaydi
'''



def check_and_send_notifications():
    today = timezone.now().date()
    if cache.get("notification_lock_for_check_and_send_notifications"):
        print(f"check_and_send_notifications cronjob | Ish davom etmoqda {today}")
        return

    cache.set("notification_lock_for_check_and_send_notifications", True, timeout=1200)  # 1200 sekunddan keyin avtomatik o'chadi
    try:
        with transaction.atomic():

            notified_ids = set()
            counter = 0
            now = timezone.now()
            points = Answer.objects.select_for_update(skip_locked=True).filter(
                is_submit_notification=False,
                notification_planned_date__lte=now,
                submission_deadline__gt=now,
            )
            print('-----points',points)
            # print('points', points)

            # print(f"check_and_send_notifications cronjob | notification yuborilmoqda {today}")
            for point in points:

                student_telegram_bot = User.objects.filter(id=point.student_id, telegram_id__isnull=False).first()
                if not student_telegram_bot:
                    continue
                print('point bor student_telegram_bot', student_telegram_bot)
                if student_telegram_bot:
                    tg_chat_id = student_telegram_bot.telegram_id
                    print('chat_id bor', tg_chat_id)
                    # Bitta chat_id ga 2 marta yuborilmasin
                    if tg_chat_id in notified_ids:
                        continue
                    notified_ids.add(tg_chat_id)

                    inline_keyboards = [
                    ]
                    answer_detail = AnswerDetail.objects.filter(answer=point).first()
                    survey_answer_options = SurveyAnswerOption.objects.filter(question=answer_detail.survey_question)
                    for survey_answer_option in survey_answer_options:
                        icon = "🔵"
                        if survey_answer_option.type == '1':
                            icon = "✅"
                        elif survey_answer_option.type == '3':
                            icon = "❌"
                        inline_keyboards.append({
                            'text': f"{icon} {survey_answer_option.name}",
                            "callback_data": f"dyn_start:{point.id}:{answer_detail.id}:{survey_answer_option.id}"
                        })

                    # success = async_to_sync(send_telegram_notification)(tg_chat_id, answer_detail.get_question_context_name, survey_answer_options)
                    success = async_to_sync(send_telegram_notification)(tg_chat_id, answer_detail.get_question_context_name, inline_keyboards)
                    print(success, 'success')
                    if success:
                        print("success bo'ldi")
                        print(inline_keyboards)
                        print('---------------------')
                    #     point.is_submit_notification = True
                    #     point.notification_sent_at = timezone.now()
                    #     point.save()

                    counter += 1
                    if counter % 30 == 0:
                        time.sleep(1)

    except IntegrityError as e:
        handle_exception(e)  # Masalan: "Bu foydalanuvchi allaqachon mavjud"
    except ValidationError as e:
        handle_exception(e)  # Masalan: "Noto'g'ri ma'lumot kiritildi"
    except Exception as e:
        handle_exception(e)  # Boshqa kutilmagan xatolar

    finally:
        # Lockni olib tashlaymiz
        cache.delete("notification_lock_for_check_and_send_notifications")
        print(f"check_and_send_notifications cronjob | yuborish yakunlandi {today}")


def check_and_send_notifications_old():
    today = timezone.now().date()
    if cache.get("notification_lock_for_check_and_send_notifications"):
        print(f"check_and_send_notifications cronjob | Ish davom etmoqda {today}")
        return

    cache.set("notification_lock_for_check_and_send_notifications", True, timeout=1200)  # 1200 sekunddan keyin avtomatik o'chadi
    try:
        with transaction.atomic():

            notified_ids = set()
            counter = 0
            now = timezone.now()
            points = Answer.objects.select_for_update(skip_locked=True).filter(
                is_submit_notification=False,
                notification_planned_date__lte=now,
                submission_deadline__gt=now,
            )
            # print('points', points)

            print(f"check_and_send_notifications cronjob | notification yuborilmoqda {today}")
            for point in points:

                student_telegram_bot = User.objects.filter(id=point.student_id, telegram_id__isnull=False).first()
                if not student_telegram_bot:
                    continue
                if student_telegram_bot:
                    tg_chat_id = student_telegram_bot.telegram_id
                    # Bitta chat_id ga 2 marta yuborilmasin
                    if tg_chat_id in notified_ids:
                        continue
                    notified_ids.add(tg_chat_id)
                    message = (
                        "🔔 So'rovnoma\n\n"
                        # f"<b>{point.schedule.employee.full_name()}</b> ustozingizni,\n"
                        f"1/4. Pedagog <b>{point.schedule.employee.full_name}</b> \n«<b>{point.schedule.subject.name}</b>» fanidan darsga keldimi?\n"
                        "(ovoz berish majburiy va anonimlik saqlanib qoladi)\n\n"
                        "👉 Pastdagi tugmalardan birini tanlang."
                        # "3 – qoniqarli\n"
                        # "4 – yaxshi\n"
                        # "5 – a’lo</blockquote>"
                    )
                    inline_keyboards = [
                        {"text": '✅ Ha', "callback_data": f"teacher:step1:yes:{schedule_point_id}:schedule:{schedule_id}"},
                        {"text": "❌ Yo‘q", "callback_data": f"teacher:step1:no:{schedule_point_id}:schedule:{schedule_id}"}
                    ]
                    success = async_to_sync(send_telegram_notification)(tg_chat_id, message, point.id, point.schedule.id)
                    if success:
                        point.is_submit_notification = True
                        point.notification_sent_at = timezone.now()
                        point.save()

                    counter += 1
                    if counter % 30 == 0:
                        time.sleep(1)

    except IntegrityError as e:
        handle_exception(e)  # Masalan: "Bu foydalanuvchi allaqachon mavjud"
    except ValidationError as e:
        handle_exception(e)  # Masalan: "Noto'g'ri ma'lumot kiritildi"
    except Exception as e:
        handle_exception(e)  # Boshqa kutilmagan xatolar

    finally:
        # Lockni olib tashlaymiz
        cache.delete("notification_lock_for_check_and_send_notifications")
        print(f"check_and_send_notifications cronjob | yuborish yakunlandi {today}")
