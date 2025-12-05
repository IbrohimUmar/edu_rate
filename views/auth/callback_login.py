from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import redirect

from services.handle_exception import handle_exception
from services.notification import send_message, notify_trancaction_error
from views.auth.client import oAuth2Client
from config.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHORIZE_URL, TOKEN_URL, RESOURCE_OWNER_URL


def auth_callback_login(request):
    auth_code = request.GET.get('code', None)
    if not auth_code:
        messages.error(request, "Sizda xatolik mavjud")
        return redirect("login")
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
        try:
            with transaction.atomic():
                email = user_details['student_id_number'] + "@namdu.uz"
                print(user_details)
                # send_message(user_details)
                notify_trancaction_error('test call back', user_details)
                # user, create = User.objects.update_or_create(hemis_id_number=user_details['student_id_number'], defaults={
                #     'first_name': user_details['firstname'],
                #     'last_name': user_details['surname'],
                #     'is_active': True,
                #     'is_staff': False,
                #     'email': email,
                #     # 'is_staff': is_staff,
                #     'mobile': user_details['phone'],
                #     'image': user_details['picture'],
                #     'user_type': '2',
                #     'birth_date': convert_date_format(user_details['birth_date']),
                #     'passport_number': user_details['passport_number'],
                #     'passport_pin': user_details['passport_pin'],
                #     'hemis_id_number': user_details['student_id_number'],
                # })
                # student_data = user_details['data']
                # student_status = get_obj_or_create(
                #     StudentStatus,
                #     student_data['studentStatus']['code'],
                #     student_data['studentStatus']['name']
                # )
                # education_form = get_obj_or_create(
                #     EducationForm,
                #     student_data['educationForm']['code'],
                #     student_data['educationForm']['name']
                # )
                # education_type = get_obj_or_create(
                #     EducationType,
                #     student_data['educationType']['code'],
                #     student_data['educationType']['name']
                # )
                # payment_form = get_obj_or_create(
                #     PaymentForm,
                #     student_data['paymentForm']['code'],
                #     student_data['paymentForm']['name']
                # )
                # # student_type = get_obj_or_create(
                # # StudentType,
                # # student_data['studentType']['code'],
                # # student_data['studentType']['name']
                # # )
                # education_lang = get_obj_or_create(
                #     EducationLang,
                #     student_data['educationLang']['code'],
                #     student_data['educationLang']['name']
                # )
                # specialty, create = Specialty.objects.get_or_create(
                #     hemis_id=student_data['specialty']['code'],
                #     defaults={
                #         "name": student_data['specialty']['name'],
                #         "code": student_data['specialty']['code'],
                #     }
                # )
                # group = get_obj_or_create_group(
                #     student_data['group']['id'],
                #     student_data['group']['name'],
                #     student_data['group']['educationLang']
                # )
                # level = get_obj_or_create(
                #     StudentLevel,
                #     student_data['level']['code'],
                #     student_data['level']['name']
                # )
                # student_department = DepartmentList.objects.get(
                #     dep_id=student_data['faculty']['id']
                # )
                # student_hemis_id = user_details['id']
                # get_or_create_student_data(
                #     user=user,
                #     student_status=student_status,
                #     education_form=education_form,
                #     student_type=None,
                #     education_type=education_type,
                #     payment_form=payment_form,
                #     education_lang=education_lang,
                #     specialty=specialty,
                #     group=group,
                #     level=level,
                #     student_department=student_department,
                #     student_hemis_id=student_hemis_id,
                # )
                # login(request, user)
                # messages.success(request, f"{user.first_name.title()}, Hemis tizimi orqali kirdingiz!")
                return redirect("home")
        except IntegrityError as e:
            handle_exception(e)
            messages.error(request, f"Saqlashda xatolik yuzaga keldi {e}")
            return redirect('home')
    else:
        print('access_token_response :', access_token_response)
        messages.error(request, "Token vaqt tugadi, qayta urining")
        return redirect("login")
