import traceback
from email.policy import default

import requests
from django.db import transaction, IntegrityError
from datetime import datetime, timedelta
import time
import pytz
from django.utils import timezone
from requests import Timeout, RequestException

from config.settings import HEMIS_URL, HEMIS_API_TOKEN
from models.models.meta import Subject, Semester, EducationYear, EducationLang, Group, Department, StructureType, \
    TrainingType, LessonPair, AuditoriumType, Building, Auditorium
from models.models.schedule import Schedule
from models.models.user import User
from services.handle_exception import handle_exception
from services.schedule.schedule_point import create_schedule_point
from services.sync_hemis.student import get_obj_or_create
from services.timestamp_to_datetime import timestamp_to_datetime

employee_list_url_hemis = f"{HEMIS_URL}/rest/v1/data/schedule-list"
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {HEMIS_API_TOKEN}',
}

def get_schedule_list(page=1, limit=20, _faculty="", _group="", _week="", _semester="", _education_year="",
                      _subject="",_employee="", _auditorium="", _lesson_pair="", lesson_date_from="", lesson_date_to=""):
    params = (f"?page={page}&limit={limit}&_faculty={_faculty}&_group={_group}"
              f"&_week={_week}&_semester={_semester}&_education_year={_education_year}&_subject={_subject}"
              f"&_employee={_employee}&_auditorium={_auditorium}&_lesson_pair={_lesson_pair}&lesson_date_from={lesson_date_from}&lesson_date_to={lesson_date_to}")
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



def schedule_sync():
    page = 1
    limit = 100
    total_count = None
    tz = pytz.timezone("Asia/Tashkent")

    today = timezone.localtime(timezone.now()).date()  # bugünün tarihi (Tashkent'e göre)
    from_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=tz)
    to_date = datetime.combine(today, datetime.max.time()).replace(tzinfo=tz)

    # from_date = datetime.today().date()  # bugünün tarihi (sadece tarih kısmı)
    # to_date = from_date + timedelta(days=2)  # 1 ay sonrası (30 gün ekledik)
    from_date_unix = int(time.mktime(from_date.timetuple()))
    to_date_unix = int(time.mktime(to_date.timetuple()))
    tz = pytz.timezone("Asia/Tashkent")

    print(f'schedule_sync cronjob | unix{from_date_unix}, {to_date_unix}')
    while total_count is None or (page - 1) * limit < total_count:
        response = get_schedule_list(page=page, limit=limit, lesson_date_from=from_date_unix,
                                     lesson_date_to=to_date_unix)
        # response = get_schedule_list(page=page, limit=limit, _group=2147, lesson_date_from=from_date_unix, lesson_date_to=to_date_unix)
        # response = get_schedule_list(page=page, limit=limit)
        data = response['data']
        total_count = data['pagination']['totalCount']
        print(data['pagination'])
        try:
            with transaction.atomic():
                for a in response['data']['items']:
                    subject, update = Subject.objects.update_or_create(
                        code=a['subject']['code'],
                        defaults={
                            'hemis_id': a['subject']['id'],
                            'name': a['subject']['name'],
                        }
                    )

                    # subject = Subject.objects.filter(code=a['subject']['code']).first()
                    # if not subject:
                    #     subject, update = Subject.objects.update_or_create(
                    #         name=a['subject']['name'],
                    #         code=a['subject']['code'],
                    #         hemis_id=a['subject']['id'],
                    #     )
                    #     # subject = Subject.objects.create(
                    #     #     code=a['subject']['code'],
                    #     #     name=a['subject']['name']
                    #     # )

                    semester = get_obj_or_create(Semester, a['semester']['code'],
                                                 a['semester']['name'])

                    education_year, update = EducationYear.objects.update_or_create(code=a['educationYear']['code'],
                                                                                    name=a['educationYear']['name'],
                                                                                    defaults={
                                                                                        'current': a['educationYear'][
                                                                                            'current']})

                    education_lang = get_obj_or_create(EducationLang, a['group']['educationLang']['code'],
                                                       a['group']['educationLang']['name'])
                    # group, update = Group.objects.update_or_create(hemis_id=a['group']['id'],
                    #                                                     defaults={
                    #                                                         'name': a['group']['name'],
                    #                                                         'education_Lang': education_lang,
                    #                                                     })
                    group = Group.objects.filter(hemis_id=a['group']['id']).first()
                    if group:
                        group.name = a['group']['name']
                        group.education_Lang = education_lang
                        group.save()
                    else:
                        group = Group.objects.create(
                            hemis_id=a['group']['id'],
                            name=a['group']['name'],
                            education_Lang=education_lang
                        )
                    faculty, create = Department.objects.get_or_create(
                        hemis_id=a['faculty']['id'], code=a['faculty']['code'],
                        defaults={
                            'structureType': get_obj_or_create(StructureType, a['faculty']['structureType']['code'],
                                                               a['faculty']['structureType']['name']),
                            'name': a['faculty']['name'],
                            'is_active': a['faculty']['active'],
                        }
                    )
                    department = None
                    if a['department']:
                        department, create = Department.objects.get_or_create(
                            hemis_id=a['department']['id'], code=a['department']['code'],
                            defaults={
                                'structureType': get_obj_or_create(StructureType,
                                                                   a['department']['structureType']['code'],
                                                                   a['department']['structureType']['name']),
                                'name': a['department']['name'],
                                'is_active': a['department']['active'],
                                'parent': faculty
                            }
                        )

                    auditorium_type = get_obj_or_create(AuditoriumType, a['auditorium']['auditoriumType']['code'],
                                                        a['auditorium']['auditoriumType']['name'])
                    building, update = Building.objects.update_or_create(hemis_id=a['auditorium']['building']['id'],
                                                                         name=a['auditorium']['building']['name'])
                    auditorium, update = Auditorium.objects.update_or_create(
                        code=a['auditorium']['code'],
                        defaults={
                            'volume': a['auditorium']['volume'],
                            'name': a['auditorium']['name'],
                            'building': building,
                            'auditorium_type': auditorium_type,
                        }
                    )

                    training_type = get_obj_or_create(TrainingType, a['trainingType']['code'],
                                                      a['trainingType']['name'])

                    lesson_pair, update = LessonPair.objects.update_or_create(code=a['lessonPair']['code'],
                                                                              name=a['lessonPair']['name'],
                                                                              start_time=a['lessonPair']['start_time'],
                                                                              end_time=a['lessonPair']['end_time'],
                                                                              education_year=education_year,
                                                                              )


                    employee = User.objects.get(hemis_id=a['employee']['id'])

                    # lesson_date = timestamp_to_datetime(a['lesson_date']).date()
                    # start_hour, start_minute = map(int, a['lessonPair']['start_time'].split(":"))
                    # lesson_start_datetime = datetime.combine(lesson_date, datetime.min.time()).replace(
                    #     hour=start_hour, minute=start_minute
                    # )
                    lesson_date = timestamp_to_datetime(a['lesson_date']).date()
                    start_hour, start_minute = map(int, a['lessonPair']['start_time'].split(":"))
                    naive_datetime = datetime.combine(lesson_date, datetime.min.time()).replace(
                        hour=start_hour, minute=start_minute
                    )
                    # 🔑 burada timezone ekliyoruz
                    lesson_start_datetime = tz.localize(naive_datetime)

                    schedule, update = Schedule.objects.update_or_create(
                        hemis_id=a['id'],
                        defaults={
                            'subject': subject,
                            'semester': semester,
                            'education_year': education_year,
                            'group': group,
                            'faculty': faculty,
                            'department': department,
                            'training_type': training_type,
                            'lesson_pair': lesson_pair,
                            'employee': employee,
                            'week': a['_week'],
                            'week_start_time': timestamp_to_datetime(a['weekStartTime']),
                            'week_end_time': timestamp_to_datetime(a['weekEndTime']),
                            'lesson_date': lesson_start_datetime,
                        }
                    )
                page += 1
        except IntegrityError as e:
            handle_exception(e)
            return False
        except Exception as e:
            handle_exception(e)
        # finally:
        #     print(f'Successfully updated schedule : {from_date}')
    create_schedule_point()
    return True



def schedule_last_seven_days_sync():
    page = 1
    limit = 100
    total_count = None
    tz = pytz.timezone("Asia/Tashkent")

    today = timezone.localtime(timezone.now()).date()
    from_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=tz)
    to_date = datetime.combine(today + timedelta(days=7), datetime.max.time()).replace(tzinfo=tz)

    from_date_unix = int(time.mktime(from_date.timetuple()))
    to_date_unix = int(time.mktime(to_date.timetuple()))

    print(f'schedule_sync cronjob | unix from={from_date_unix}, to={to_date_unix}')

    while total_count is None or (page - 1) * limit < total_count:
        response = get_schedule_list(
            page=page,
            limit=limit,
            lesson_date_from=from_date_unix,
            lesson_date_to=to_date_unix,
        )
        data = response['data']
        total_count = data['pagination']['totalCount']
        print(f'schedule_sync_seven days pagination | {data['pagination']}')
        for a in data['items']:
            try:
                # 🔸 har bir yozuvni o'zining kichik transaction ichida saqlaymiz
                with transaction.atomic():
                    subject, _ = Subject.objects.update_or_create(
                        code=a['subject']['code'],
                        defaults={
                            'hemis_id': a['subject']['id'],
                            'name': a['subject']['name'],
                        },
                    )

                    semester = get_obj_or_create(
                        Semester,
                        a['semester']['code'],
                        a['semester']['name'],
                    )

                    education_year, _ = EducationYear.objects.update_or_create(
                        code=a['educationYear']['code'],
                        name=a['educationYear']['name'],
                        defaults={'current': a['educationYear']['current']},
                    )

                    education_lang = get_obj_or_create(
                        EducationLang,
                        a['group']['educationLang']['code'],
                        a['group']['educationLang']['name'],
                    )

                    group, _ = Group.objects.update_or_create(
                        hemis_id=a['group']['id'],
                        defaults={
                            'name': a['group']['name'],
                            'education_Lang': education_lang,
                        },
                    )

                    faculty, _ = Department.objects.update_or_create(
                        hemis_id=a['faculty']['id'],
                        code=a['faculty']['code'],
                        defaults={
                            'structureType': get_obj_or_create(
                                StructureType,
                                a['faculty']['structureType']['code'],
                                a['faculty']['structureType']['name'],
                            ),
                            'name': a['faculty']['name'],
                            'is_active': a['faculty']['active'],
                        },
                    )

                    department = None
                    if a.get('department'):
                        department, _ = Department.objects.update_or_create(
                            hemis_id=a['department']['id'],
                            code=a['department']['code'],
                            defaults={
                                'structureType': get_obj_or_create(
                                    StructureType,
                                    a['department']['structureType']['code'],
                                    a['department']['structureType']['name'],
                                ),
                                'name': a['department']['name'],
                                'is_active': a['department']['active'],
                                'parent': faculty,
                            },
                        )

                    auditorium_type = get_obj_or_create(
                        AuditoriumType,
                        a['auditorium']['auditoriumType']['code'],
                        a['auditorium']['auditoriumType']['name'],
                    )

                    building, _ = Building.objects.update_or_create(
                        hemis_id=a['auditorium']['building']['id'],
                        defaults={'name': a['auditorium']['building']['name']},
                    )

                    auditorium, _ = Auditorium.objects.update_or_create(
                        code=a['auditorium']['code'],
                        defaults={
                            'volume': a['auditorium']['volume'],
                            'name': a['auditorium']['name'],
                            'building': building,
                            'auditorium_type': auditorium_type,
                        },
                    )

                    training_type = get_obj_or_create(
                        TrainingType,
                        a['trainingType']['code'],
                        a['trainingType']['name'],
                    )

                    lesson_pair, _ = LessonPair.objects.update_or_create(
                        code=a['lessonPair']['code'],
                        defaults={
                            'name': a['lessonPair']['name'],
                            'start_time': a['lessonPair']['start_time'],
                            'end_time': a['lessonPair']['end_time'],
                            'education_year': education_year,
                        },
                    )

                    employee = User.objects.get(hemis_id=a['employee']['id'])

                    lesson_date = timestamp_to_datetime(a['lesson_date']).date()
                    start_hour, start_minute = map(int, a['lessonPair']['start_time'].split(":"))
                    naive_datetime = datetime.combine(lesson_date, datetime.min.time()).replace(
                        hour=start_hour, minute=start_minute
                    )
                    lesson_start_datetime = tz.localize(naive_datetime)

                    Schedule.objects.update_or_create(
                        hemis_id=a['id'],
                        defaults={
                            'subject': subject,
                            'semester': semester,
                            'education_year': education_year,
                            'group': group,
                            'faculty': faculty,
                            'department': department,
                            'training_type': training_type,
                            'lesson_pair': lesson_pair,
                            'employee': employee,
                            'week': a['_week'],
                            'week_start_time': timestamp_to_datetime(a['weekStartTime']),
                            'week_end_time': timestamp_to_datetime(a['weekEndTime']),
                            'lesson_date': lesson_start_datetime,
                        },
                    )

            except IntegrityError as e:
                handle_exception(e)
            except Exception as e:
                handle_exception(e)

        page += 1
        time.sleep(0.3)

    print(f'Successfully updated last 7-day schedule ({from_date} → {to_date})')
    return True

