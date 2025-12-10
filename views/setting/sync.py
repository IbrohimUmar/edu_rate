import threading
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from services.handle_exception import handle_exception
from services.schedule.schedule_point import create_schedule_answer
from services.schedule.schedule_point_notify import check_and_send_notifications
# 🔸 Sen ishlatadigan sync funksiyalar
from services.sync_hemis.employee import employee_sync
from services.sync_hemis.student import student_sync
from services.sync_hemis.schedule import schedule_sync, schedule_last_seven_days_sync
# ===========================================================
# 🔹 GLOBAL LOCK VA STATUS
# ===========================================================

# faqat bitta umumiy lock — hammasi uchun
global_lock = threading.Lock()

# hozirda qaysi sync ishlayapti
current_sync_type = {"name": None}


# ===========================================================
# 🔹 Thread ichida xavfsiz ishga tushirish funksiyasi
# ===========================================================

def run_in_thread(target_func, sync_type):
    """Bir vaqtning o‘zida faqat bitta sinxronizatsiyani ishga tushiradi."""
    if not global_lock.acquire(blocking=False):  # Agar band bo‘lsa
        return False  # boshqa sync davom etayapti

    def run():
        try:
            current_sync_type["name"] = sync_type
            print(f"➡️  {sync_type} sinxronizatsiyasi boshlandi")
            target_func()  # sinxronlash funksiyasi
            print(f"✅  {sync_type} sinxronizatsiyasi tugadi")
        except Exception as e:
            print(f"❌ {sync_type} sinxronizatsiyada xato:", e)
            handle_exception(e, False)
        finally:
            current_sync_type["name"] = None
            global_lock.release()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return True


# ===========================================================
# 🔹 DJANGO VIEW
# ===========================================================

@login_required(login_url='login')
def setting_sync(request):
    """Sinxronizatsiya boshqaruv sahifasi."""
    sync_employee = request.GET.get('sync_employee')
    sync_student = request.GET.get('sync_student')
    sync_schedule = request.GET.get('sync_schedule')
    sync_schedule_seven_day = request.GET.get('sync_schedule_seven_day')
    check_and_send_notification = request.GET.get('check_and_send_notification')
    create_schedule_answer_sync = request.GET.get('create_schedule_answer')

    if sync_employee is not None:
        if run_in_thread(employee_sync, "employee"):
            messages.success(request, "👷‍♂️ O'qituvchilar sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, f"⚠️ '{current_sync_type['name']}' sinxronizatsiyasi hali tugamagan!")

    if sync_student is not None:
        if run_in_thread(student_sync, "student"):
            messages.success(request, "🎓 Talabalar sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, f"⚠️ '{current_sync_type['name']}' sinxronizatsiyasi hali tugamagan!")

    if sync_schedule is not None:
        if run_in_thread(schedule_sync, "schedule"):
            messages.success(request, "📘 O'quv rejalar sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, f"⚠️ '{current_sync_type['name']}' sinxronizatsiyasi hali tugamagan!")

    if sync_schedule_seven_day is not None:
        if run_in_thread(schedule_last_seven_days_sync, "sync_schedule_seven_day"):
            messages.success(request, "📘 O'quv rejalar - kunlik sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, f"⚠️ '{current_sync_type['name']}' sinxronizatsiyasi hali tugamagan!")


    if create_schedule_answer_sync is not None:
        if run_in_thread(create_schedule_answer, "create_schedule_answer"):
            messages.success(request, "So'rovnomalar uchun javob yaratish boshlandi - Notification yuborish func.")
        else:
            messages.warning(request, f"⚠️ '{current_sync_type['name']}' sinxronizatsiyasi hali tugamagan!")



    if check_and_send_notification is not None:
        if run_in_thread(check_and_send_notifications, "check_and_send_notification"):
            messages.success(request, "📘 Notification yuborish - Notification yuborish func.")
        else:
            messages.warning(request, f"⚠️ '{current_sync_type['name']}' sinxronizatsiyasi hali tugamagan!")



    if request.GET:
        return redirect("setting_sync")

    context = {"current_sync": current_sync_type["name"]}
    return render(request, "setting/sync.html", context)
