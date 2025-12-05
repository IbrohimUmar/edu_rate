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


def validate_telegram_initdata(init_data: str) -> dict | None:
    from urllib.parse import parse_qs
    import hmac
    import hashlib
    import time
    import json
    from config.settings import TG_BOT_TOKEN
    BOT_TOKEN = '8465213062:AAEN_kDqx2EvYlpy0WVton20UBOEuKlhF6k'  # settings.py'ye koy
    """Telegram initData doğrulama – resmi yöntem"""
    try:
        parsed = parse_qs(init_data)

        received_hash = parsed.pop("hash")[0]

        # Alfabetik sırala ve data_check_string oluştur
        data_check_string = "\n".join(f"{k}={v[0]}" for k, v in sorted(parsed.items()))

        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash != received_hash:
            return None

        # auth_date eski mi kontrolü (opsiyonel ama önerilir)
        auth_date = int(parsed["auth_date"][0])
        if (time.time() - auth_date) > 86400:  # 24 saat
            return None

        user_json = parsed["user"][0]
        user = json.loads(user_json)
        return user

    except Exception:
        return None

def get_gender(gender):
    if gender['code'] == '12':
        return '2'
    elif gender['code'] == '11':
        return '1'


def auth_callback_login(request):
    auth_code = request.GET.get('code', None)
    if not auth_code:
        messages.error(request, "Sizda xatolik mavjud")
        return redirect("login")

    init_data = request.GET.get("tgWebAppData", "")
    # if not init_data:
    #     messages.error(request, "telegram datalar mavjud emas")
    #     return redirect('login')
    #
    telegram_data = validate_telegram_initdata(init_data)
    # if not telegram_data:
    #     messages.error(request, "telegram datalar valid emas")
    #     return redirect('login')
    # telegram_id = telegram_data["id"]




    print('keldi')
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
    if 'access_token' in access_token_response:
        access_token = access_token_response['access_token']
        user_details = client.get_user_details(access_token)

        notify_trancaction_error('test call back', user_details)
        notify_trancaction_error('test init_data', init_data)
        notify_trancaction_error('test telegram_data', telegram_data)
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
