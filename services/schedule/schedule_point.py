from django.utils import timezone
from django.db import IntegrityError, transaction
from datetime import datetime, timedelta
import pytz

from models.models.schedule import Schedule
from models.models.schedule_point import SchedulePoint
from models.models.student_meta import StudentMeta
from services.handle_exception import handle_exception


def calculate_deadline(datetime_input: datetime, start_time_str: str) -> datetime:
    hour, minute = map(int, start_time_str.split(":"))
    # Günü koruyarak saat ve dakikayı ekle
    start_datetime = datetime_input.replace(hour=hour, minute=minute, second=0, microsecond=0)
    # 48 saat ekle
    deadline = start_datetime + timedelta(hours=48)
    return deadline


def calculate_lesson_end_time(datetime_input: datetime, end_time_str: str) -> datetime:
    # Asia/Tashkent timezone nesnesi
    tz = pytz.timezone('Asia/Tashkent')

    # Eğer datetime_input timezone-aware değilse (naive ise), timezone ata
    if datetime_input.tzinfo is None:
        datetime_input = tz.localize(datetime_input)
    else:
        # UTC gibi başka bir saat dilimindeyse, Tashkent'e çevir
        datetime_input = datetime_input.astimezone(tz)

    # Saati ve dakikayı ayarla
    hour, minute = map(int, end_time_str.split(":"))
    start_datetime = datetime_input.replace(hour=hour, minute=minute, second=0, microsecond=0)

    return start_datetime



def calculate_50_min_later(datetime_input: datetime, start_time_str: str) -> datetime:
    # Asia/Tashkent timezone nesnesi
    tz = pytz.timezone('Asia/Tashkent')

    # Eğer datetime_input timezone-aware değilse (naive ise), timezone ata
    if datetime_input.tzinfo is None:
        datetime_input = tz.localize(datetime_input)
    else:
        # UTC gibi başka bir saat dilimindeyse, Tashkent'e çevir
        datetime_input = datetime_input.astimezone(tz)

    # Saati ve dakikayı ayarla
    hour, minute = map(int, start_time_str.split(":"))
    start_datetime = datetime_input.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # 50 dakika ekle
    result = start_datetime + timedelta(minutes=50)
    return result

'''
func vazifasi quyidagicha
o'quv rejalarini olib belgilangan sana oralig'idagilarni
talabalar darsni baholashlari kerakligi uchun harbir o'quv rejasiga SchedulePoint yaratib chiqadi
va dars boshlanganiga 40 daqiqa bo'lganida esa boshqa bir func orqali SchedulePoint dagi message talabaga yuboriladi

har 3 kunda 1 marta ishlaydi
'''

def create_schedule_point():
    now = timezone.now()
    schedules = Schedule.objects.filter(
        lesson_date__date=now.date(),   # sadece bugünkü dersi alsın
        lesson_date__gt=now)
    '''
    1. haftalik schedule ni oladi
    va harbir tg botdan ro'yxatdan o'tgan talabaga create qilib chiqadi yuborish mas faqat create
    '''
    try:
        with transaction.atomic():
            for schedule in schedules:
                student_meta_qs = StudentMeta.objects.filter(student_status__code='11',
                                                      group=schedule.group,
                                                      user__telegram_id__isnull=False
                                                      )
                for data in student_meta_qs:
                    schedule_point, created = SchedulePoint.objects.update_or_create(
                        student=data.user,
                        schedule=schedule,
                        defaults={
                            'employee':schedule.employee,
                            'submission_deadline': calculate_deadline(
                                schedule.lesson_date, schedule.lesson_pair.start_time
                            ),
                            'notification_planned_date': calculate_lesson_end_time(
                                schedule.lesson_date, schedule.lesson_pair.end_time
                            )
                        }
                    )
                schedule.is_create_schedule_point = True
                schedule.save()

    except IntegrityError as e:
        handle_exception(e)
    except Exception as e:
        handle_exception(e)
    print(f"create_schedule_point cronjob | muvaffaqiyatli yakunlandi sana {now}")


def create_schedule_point_by_student(custom_user, student):
    now = timezone.now()
    end_time = now + timedelta(days=6)   # Bitiş zamanı: bugünden 6 gün sonraya kadar (toplam 7 gün aralık)

    schedules = Schedule.objects.filter(group=student.group, lesson_date__gte=now, lesson_date__lte=end_time)

    '''
    1. shu talabaga oid o'quv rejalarni oladi
    va mavjud haftadagi qolgan darslarni create qilib chiqadi shu haftaga oid bundan oldiginlarni emas faqat qolganlarini
    '''
    try:
        with transaction.atomic():
            for schedule in schedules:
                    schedule_point, create = SchedulePoint.objects.get_or_create(
                        student=custom_user,
                        schedule=schedule,
                        defaults={
                            'employee':schedule.employee,
                            'submission_deadline':calculate_deadline(schedule.lesson_date, schedule.lesson_pair.start_time),
                            'notification_planned_date':calculate_lesson_end_time(schedule.lesson_date, schedule.lesson_pair.end_time)
                        }
                    )
    except IntegrityError as e:
        handle_exception(e)

    except Exception as e:
        handle_exception(e)
    print("Successful create_schedule_point ")
