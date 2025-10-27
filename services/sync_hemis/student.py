from django.db import transaction, IntegrityError
import requests
from models.models.meta import StudentStatus, EducationForm, EducationType, PaymentForm, StudentType, SocialCategory, \
    Specialty, StudentLevel, Department, EducationLang, Group
from models.models.student_meta import StudentMeta
from models.models.user import User
from config.settings import HEMIS_URL, HEMIS_API_TOKEN
from requests.exceptions import Timeout, RequestException

from services.handle_exception import handle_exception

student_list_url_hemis = f"{HEMIS_URL}/rest/v1/data/student-list"
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {HEMIS_API_TOKEN}',
}

def get_obj_or_create(model, code, name):
    obj = model.objects.filter(code=code).first()
    if obj:
        return obj
    return model.objects.create(code=code, name=name)


def get_obj_or_create_group(id, name, education_lang):
    edu_lang = None
    if bool(education_lang):
        edu_lang = get_obj_or_create(EducationLang, education_lang['code'], education_lang['name'])
    group = Group.objects.filter(hemis_id=id, education_Lang=edu_lang).first()
    if group:
        return group
    obj_model, create = Group.objects.get_or_create(
        hemis_id=id, education_Lang=edu_lang,defaults={"name": name}
    )
    return obj_model

def student_update_or_create_from_hemis_data(data):

    def get_gender(gender):
        if gender['code'] == '12':
            return '2'
        elif gender['code'] == '11':
            return '1'

    student = User.objects.filter(hemis_id_number=data['student_id_number']).first()
    if student:
        student.type = '3'
        # student.hemis_id = data['id']
        student.first_name = data['first_name']
        student.second_name = data['second_name']
        student.third_name = data['third_name']
        student.full_name = data['full_name']
        student.short_name = data['short_name']
        student.image = data['image']
        student.gender = get_gender(data['gender'])
        student.is_active = True
        student.save()
    else:
        student = User.objects.create(
            hemis_id_number=data['student_id_number'],
            # hemis_id=data['id'],
            type='3',
            email=f"{data['student_id_number']}@namdu.uz",
            first_name=data['first_name'],
            second_name=data['second_name'],
            third_name=data['third_name'],
            short_name=data['short_name'],
            full_name=data['full_name'],
            gender=get_gender(data['gender']),
            image=data['image'],
            is_active=True,
        )

    student_status = get_obj_or_create(StudentStatus, data['studentStatus']['code'], data['studentStatus']['name'])
    education_form = get_obj_or_create(EducationForm, data['educationForm']['code'], data['educationForm']['name'])
    education_type = get_obj_or_create(EducationType, data['educationType']['code'], data['educationType']['name'])
    payment_form = get_obj_or_create(PaymentForm, data['paymentForm']['code'], data['paymentForm']['name'])
    student_type = get_obj_or_create(StudentType, data['studentType']['code'], data['studentType']['name'])
    social_category = get_obj_or_create(SocialCategory, data['socialCategory']['code'], data['socialCategory']['name'])
    specialty, create = Specialty.objects.get_or_create(
        hemis_id=data['specialty']['id'],
        # code=data['specialty']['code'],
        defaults={
            "name": data['specialty']['name'],
            "code": data['specialty']['code'],
        }
    )
    level = get_obj_or_create(StudentLevel, data['level']['code'], data['level']['name'])
    group = get_obj_or_create_group(data['group']['id'], data['group']['name'], data['group']['educationLang'])
    student_department = Department.objects.get(hemis_id=data['department']['id'])
    student_hemis_id = data['id']
    student_data = StudentMeta.objects.update_or_create(
        user=student,
        hemis_id=data['meta_id'],
        defaults={
            "student_status": student_status,
            "education_form": education_form,
            "education_type": education_type,
            "payment_form": payment_form,
            "student_type": student_type,
            "specialty": specialty,
            "group": group,
            "level": level,
            "department": student_department,
            "hemis_id": student_hemis_id,
            'social_category': social_category,
            "is_active":True
        }
    )
    return student, student_data


def get_student_list(page=1, limit=20, _education_form="", _education_type="", _payment_form="", _department="", _group="", _specialty="", _level="", _semester="", _province="", _district="", _gender='', _citizenship='',_student_status='',search="", passport_pin='', passport_number=''):
    params = f"?page={page}&limit={limit}&_education_form={_education_form}&_education_type={_education_type}&_payment_form={_payment_form}&_department={_department}&_group={_group}&_specialty={_specialty}&_level={_level}&_semester={_semester}&_province={_province}&_district={_district}&_gender={_gender}&_citizenship={_citizenship}&_student_status={_student_status}&search={search}&passport_pin={passport_pin}&passport_number={passport_number}"
    payload = {}
    try:
        response = requests.request("GET", student_list_url_hemis + params, headers=headers, data=payload)
        response.raise_for_status()  # HTTP errors
        return response.json()
    except Timeout as e:
        handle_exception(e)
        return {"code": 408, "error": "Request timed out", 'success': False, 'data': {}}
    except RequestException as e:
        handle_exception(e)
        return {"code": 500, "error": str(e), 'success': False, 'data': {}}


def student_sync():
    page = 1
    limit = 100
    total_count = None
    active_meta_data = []
    while total_count is None or (page - 1) * limit < total_count:
        response = get_student_list(page=page, limit=limit)
        data = response['data']
        total_count = data['pagination']['totalCount']
        print(data['pagination'])
        try:
            with transaction.atomic():
                for a in response['data']['items']:
                    student_update_or_create_from_hemis_data(a)
                page += 1
        except IntegrityError as e:
            handle_exception(e)
            print(e)
            return False
    print('Successfully updated student list')
    return True
