import aiogram
import aioredis
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import async_to_sync
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction, IntegrityError
from django.shortcuts import redirect

from models.models.meta import StudentStatus, EducationForm, EducationType, PaymentForm, StudentType, EducationLang, \
    Specialty, StudentLevel, Department, StructureType, SocialCategory
from models.models.student_meta import StudentMeta
from models.models.user import User
from services.handle_exception import handle_exception
from services.notification import send_message, notify_trancaction_error
from services.sync_hemis.student import get_obj_or_create, get_obj_or_create_group
from views.auth.client import oAuth2Client
from config.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHORIZE_URL, TOKEN_URL, RESOURCE_OWNER_URL


def get_gender(gender):
    if gender['code'] == '12':
        return '2'
    elif gender['code'] == '11':
        return '1'


# def debug_oauth_log(request):
#     cookies = request.COOKIES
#     session_id = request.session.session_key
#     user_agent = request.META.get("HTTP_USER_AGENT")
#     host = request.get_host()
#
#     log_text = (
#         "🔍 *OAuth Debug Information*\n\n"
#         f"🍪 *COOKIES:* `{cookies}`\n"
#         f"🆔 *SESSION ID:* `{session_id}`\n"
#         f"📱 *USER AGENT:* `{user_agent}`\n"
#         f"🌐 *HOST:* `{host}`\n"
#     )
#
#     print(log_text)  # Terminalga chiqadi
#
#     # Agar Telegramga jo‘natmoqchi bo‘lsang:
#     # send_telegram_notification(log_text)
#
#     return log_text

async def after_login(user_info, access_token, refresh_token, bot):
    menu_kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        input_field_placeholder="Bo'limlardan birini tanlang!",
        keyboard=[
            [
                KeyboardButton(text="📰 Shaxsiy ma'lumotlar"),
                KeyboardButton(text="📝 Izoh qoldirish"),
            ],
            [
                KeyboardButton(text="🧾 Dars jadvali"),
                KeyboardButton(text="💡 Taklif"),
            ],
            [
                KeyboardButton(text="📊 Faol so‘rovnomalarim")
            ],
        ]
    )

    # Telegram mesajı gönder
    await bot.send_message(
        chat_id=user_info['chat_id'],
        text=f"🎉 <b>Tabriklaymiz, {user_info['full_name']}!</b>\n✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz.",
        reply_markup=menu_kb,
        parse_mode="HTML"
    )

    # Redis'e kaydet
    REDIS_URL = "redis://localhost:6379/1"
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

    user_id = user_info['data']['id']
    await redis.set(f"jwt:{user_id}", access_token, ex=48 * 3600)
    await redis.set(f"refresh-token:{user_id}", refresh_token, ex=7 * 24 * 3600)


def auth_callback_login(request):
    auth_code = request.GET.get('code', None)
    chat_id = request.session.get('chat_id')

    if not auth_code:
        messages.error(request, "Sizda xatolik mavjud")
        return redirect("login")
    if not chat_id:
        # logs = debug_oauth_log(request)
        # notify_trancaction_error('state mavjud emas', logs)
        messages.error(request, "call back chat id mavjud emas")
        return redirect("login")
    User.objects.filter(telegram_id=chat_id).update(telegram_id=None)
    # notify_trancaction_error('chat_id mavjud', f'state ok {chat_id}')

    client = oAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        authorize_url=AUTHORIZE_URL,
        token_url=TOKEN_URL,
        resource_owner_url=RESOURCE_OWNER_URL
    )
    access_token_response = client.get_access_token(auth_code)
    full_info = {}
    notify_trancaction_error('access_token_response mavjud', access_token_response)

    if 'access_token' in access_token_response:
        access_token = access_token_response['access_token']
        refresh_token = access_token_response['refresh_token']
        user_details = client.get_user_details(access_token)

        notify_trancaction_error('test call back', user_details)
        try:
            with transaction.atomic():
                if user_details.get("email", None) is None:
                    email = user_details['student_id_number'] + "@namdu.uz"
                else:
                    email = user_details['email']
                # send_message(user_details)
                student_data = user_details['data']

                user, create = User.objects.update_or_create(hemis_id_number=user_details['student_id_number'], defaults={
                    'first_name': student_data['first_name'],
                    'second_name': student_data['second_name'],
                    'third_name': student_data['third_name'],
                    'full_name': student_data['full_name'],
                    'short_name': student_data['short_name'],

                    'is_active': True,
                    'is_staff': False,
                    'email': email,
                    'telegram_id': chat_id,
                    # 'is_staff': is_staff,
                    'mobile': user_details['phone'],
                    'image': user_details['picture'],
                    'user_type': '3',
                    'gender': get_gender(student_data['gender']),
                })
                student_status = get_obj_or_create(
                    StudentStatus,
                    student_data['studentStatus']['code'],
                    student_data['studentStatus']['name']
                )
                education_form = get_obj_or_create(
                    EducationForm,
                    student_data['educationForm']['code'],
                    student_data['educationForm']['name']
                )
                education_type = get_obj_or_create(
                    EducationType,
                    student_data['educationType']['code'],
                    student_data['educationType']['name']
                )
                payment_form = get_obj_or_create(
                    PaymentForm,
                    student_data['paymentForm']['code'],
                    student_data['paymentForm']['name']
                )
                # student_type = get_obj_or_create(
                # StudentType,
                # student_data['studentType']['code'],
                # student_data['studentType']['name']
                # )
                education_lang = get_obj_or_create(
                    EducationLang,
                    student_data['educationLang']['code'],
                    student_data['educationLang']['name']
                )

                specialty = Specialty.objects.filter(code=student_data['specialty']['code']).first()
                if not specialty:
                    specialty, create = Specialty.objects.get_or_create(
                        code=student_data['specialty']['code'],
                        # code=data['specialty']['code'],
                        defaults={
                            "name": student_data['specialty']['name']
                        }
                    )
                social_category = get_obj_or_create(SocialCategory, student_data['socialCategory']['code'],
                                                    student_data['socialCategory']['name'])

                group = get_obj_or_create_group(student_data['group']['id'], student_data['group']['name'],
                                                student_data['group']['educationLang'])

                level = get_obj_or_create(
                    StudentLevel,
                    student_data['level']['code'],
                    student_data['level']['name']
                )
                student_department = None
                if student_data.get('faculty', None):
                    student_department, create = Department.objects.get_or_create(
                        hemis_id=student_data['faculty']['id'],
                        code=student_data['faculty']['code'],
                        defaults={
                            'structureType': get_obj_or_create(StructureType,
                                                               student_data['faculty']['structureType']['code'],
                                                               student_data['faculty']['structureType']['name']),
                            'name': student_data['faculty']['name'],
                            'is_active': student_data['faculty']['active'],
                        }
                    )
                # student_department = DepartmentList.objects.get(
                #     dep_id=student_data['faculty']['id']
                # )

                student_hemis_id = user_details['id']
                student_data, update = StudentMeta.objects.update_or_create(
                    user=user,
                    defaults={
                        "student_status": student_status,
                        "education_form": education_form,
                        "education_type": education_type,
                        "payment_form": payment_form,
                        "specialty": specialty,
                        "group": group,
                        "level": level,
                        "department": student_department,
                        'social_category': social_category,
                        "is_active": True
                    }
                )

                bot = aiogram.Bot(token="8465213062:AAEN_kDqx2EvYlpy0WVton20UBOEuKlhF6k")
                async_to_sync(after_login)({"chat_id":chat_id, 'full_name':student_data['full_name']}, access_token, refresh_token, bot)

                login(request, user)
                messages.success(request, f"{user.first_name.title()}, Hemis tizimi orqali kirdingiz!")
                return redirect("home")
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('home')
    else:
        print('access_token_response :', access_token_response)
        messages.error(request, "Token vaqt tugadi, qayta urining")
        return redirect("login")
