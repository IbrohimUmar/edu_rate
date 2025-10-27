import requests
from django.db import transaction, IntegrityError
from requests import Timeout, RequestException

from config.settings import HEMIS_URL, HEMIS_API_TOKEN
from models.models.meta import AcademicRank, AcademicDegree, Department, StructureType, StaffPosition, EmploymentForm, \
    EmploymentStaff, EmployeeStatus, EmployeeType
from models.models.user import User
from models.models.employee_meta import EmployeeMeta

import traceback
import logging
import logging

from services.handle_exception import handle_exception
from services.sync_hemis.student import get_obj_or_create
from services.timestamp_to_date import timestamp_to_date
from services.timestamp_to_datetime import timestamp_to_datetime

developer_logger = logging.getLogger('developer_logger')

logger = logging.getLogger(__name__)

employee_list_url_hemis = f"{HEMIS_URL}/rest/v1/data/employee-list"
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {HEMIS_API_TOKEN}',
}

def get_employee_list(type="", page=1, limit=20, _department="", _gender="", _staff_position="", _employment_form="", _employment_staff="", _employee_type="", _academic_rank="", _academic_degree="", passport_pin="", passport_number="", search=""):
    params = f"?type={type}&page={page}&limit={limit}&_department={_department}&_gender={_gender}&_staff_position={_staff_position}&_employment_form={_employment_form}&_employment_staff={_employment_staff}&_employee_type={_employee_type}&_academic_rank={_academic_rank}&_academic_degree={_academic_degree}&passport_pin={passport_pin}&passport_number={passport_number}&search={search}"
    payload = {}
    try:
        response = requests.request("GET", employee_list_url_hemis + params, headers=headers, data=payload)
        response.raise_for_status()  # HTTP errors
        return response.json()
    except Timeout as e:
        handle_exception(e)
        return {"code": 408, "error": "Request timed out", 'success': False, 'data': {}}
    except RequestException as e:
        handle_exception(e)
        return {"code": 500, "error": str(e), 'success': False, 'data': {}}


def employee_sync():
    page = 1
    limit = 100
    total_count = None
    active_meta_data = []
    created_hemis_ids = set()
    while total_count is None or (page - 1) * limit < total_count:
        response = get_employee_list(page=page, limit=limit)
        data = response['data']
        total_count = data['pagination']['totalCount']
        print(data['pagination'])
        try:
            with transaction.atomic():
                for a in response['data']['items']:

                        employee_custom_user = User.objects.filter(hemis_id_number=a['employee_id_number']).first()

                        if employee_custom_user:
                            # agar foydalanuvchi mavjud bo'lsa emaili yangilanmaydi
                            employee_custom_user.hemis_id = a['id']
                            employee_custom_user.first_name = a['first_name']
                            employee_custom_user.second_name = a['second_name']
                            employee_custom_user.third_name = a['third_name']
                            employee_custom_user.full_name = a['full_name']
                            employee_custom_user.short_name = a['short_name']
                            employee_custom_user.image = a['image']
                            employee_custom_user.is_staff = True
                            employee_custom_user.is_active = True
                            employee_custom_user.save()
                        elif not employee_custom_user and a['employee_id_number'] not in created_hemis_ids:
                            # mavjud bo'lmasa emasil create bo'ladi
                            employee_custom_user = User.objects.create(
                                hemis_id=a['id'],
                                hemis_id_number=a['employee_id_number'],
                                type='2',
                                email=f"{a['employee_id_number']}@namdu.uz",  # Yeni kullanıcı için email oluştur
                                first_name=a['first_name'],
                                second_name=a['second_name'],
                                third_name=a['third_name'],
                                full_name=a['full_name'],
                                short_name=a['short_name'],
                                image=a['image'],
                                is_staff=True,
                                is_active=True,
                            )
                            created_hemis_ids.add(a['employee_id_number'])

                        custom_user, meta = employee_meta_update_or_create(employee_custom_user, a)
                        active_meta_data.append(a['meta_id'])
                page += 1
        except IntegrityError as e:
            handle_exception(e)

    EmployeeMeta.objects.exclude(meta_id__in=active_meta_data).update(is_active=False)
    print('Successfully updated employee list')
    return True





def employee_meta_update_or_create(employee_custom_user, employee):

    academic_degree = get_obj_or_create(
        AcademicDegree,
        employee['academicDegree']['code'],
        employee['academicDegree']['name']
    )
    academic_rank = get_obj_or_create(
        AcademicRank,
        employee['academicRank']['code'],
        employee['academicRank']['name']
    )
    department, create = Department.objects.get_or_create(
        hemis_id=employee['department']['id'], code=employee['department']['code'],
        defaults={
            'structureType': get_obj_or_create(StructureType, employee['department']['structureType']['code'], employee['department']['structureType']['name']),
            'name': employee['department']['name'],
            'is_active': employee['department']['active'],
        }
    )
    staff_position = get_obj_or_create(
        StaffPosition,
        employee['staffPosition']['code'],
        employee['staffPosition']['name']
    )
    employment_form = get_obj_or_create(
        EmploymentForm,
        employee['employmentForm']['code'],
        employee['employmentForm']['name']
    )
    employment_staff = get_obj_or_create(
        EmploymentStaff,
        employee['employmentStaff']['code'],
        employee['employmentStaff']['name']
    )
    employee_status = get_obj_or_create(
        EmployeeStatus,
        employee['employeeStatus']['code'],
        employee['employeeStatus']['name']
    )
    employee_type = get_obj_or_create(
        EmployeeType,
        employee['employeeType']['code'],
        employee['employeeType']['name']
    )
    employee_meta, create = EmployeeMeta.objects.update_or_create(
        meta_id=employee['meta_id'],
        defaults={
            'user': employee_custom_user,
            'academic_degree': academic_degree,
            'academic_rank': academic_rank,
            'department': department,
            'employment_form': employment_form,
            'employment_staff': employment_staff,
            'staff_position': staff_position,
            'employee_status': employee_status,
            'employee_type': employee_type,
            'contract_number': employee['contract_number'],
            'decree_number': employee['decree_number'],
            'contract_date': timestamp_to_date(employee['contract_date']),
            'decree_date': timestamp_to_date(employee['decree_date']),
            'hemis_created_at': timestamp_to_datetime(employee['created_at']),
            'hemis_updated_at': timestamp_to_datetime(employee['updated_at']),
            'is_active': True,
        }
    )
    return employee_custom_user, employee_meta