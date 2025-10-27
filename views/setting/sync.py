import threading

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from models.models.student_meta import StudentMeta
from models.models.employee_meta import EmployeeMeta
from services.handle_exception import handle_exception
from services.sync_hemis.employee import employee_sync
from services.sync_hemis.schedule import schedule_sync
from services.sync_hemis.student import student_sync


@login_required(login_url='login')
def setting_sync(request):
    """Sinxronizatsiya boshqaruv sahifasi."""
    sync_employee = request.GET.get('sync_employee')
    sync_student = request.GET.get('sync_student')
    sync_schedule = request.GET.get('sync_schedule')

    # O‘qituvchi sinxronizatsiyasi
    if sync_employee is not None:
        if run_in_thread(employee_sync, "employee"):
            messages.success(request, "👷‍♂️ O'qituvchilar sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, "⚠️ O'qituvchilar sinxronizatsiyasi hali tugamagan!")

    # Talaba sinxronizatsiyasi
    if sync_student is not None:
        if run_in_thread(student_sync, "student"):
            messages.success(request, "🎓 Talabalar sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, "⚠️ Talabalar sinxronizatsiyasi hali tugamagan!")

    # O‘quv reja sinxronizatsiyasi
    if sync_schedule is not None:
        if run_in_thread(schedule_sync, "schedule"):
            messages.success(request, "📘 O'quv rejalar sinxronizatsiyasi boshlandi.")
        else:
            messages.warning(request, "⚠️ O'quv rejalar sinxronizatsiyasi hali tugamagan!")

    # So‘rovdan keyin qayta yo‘naltirish
    if request.GET:
        return redirect("setting_sync")

    # Template konteksti
    context = {"sync_status": sync_status}
    return render(request, "setting/sync.html", context)




# ===========================================================
# 🔹 Global boshqaruv: Lock va holat
# ===========================================================

sync_locks = {
    "employee": threading.Lock(),
    "student": threading.Lock(),
    "schedule": threading.Lock(),
}

sync_status = {
    "employee": False,
    "student": False,
    "schedule": False,
}


# ===========================================================
# 🔹 Thread ichida xavfsiz ishlovchi yordamchi funksiya
# ===========================================================

def run_in_thread(target_func, sync_type):
    """Sinxronizatsiyani yangi thread ichida ishga tushiradi."""
    lock = sync_locks[sync_type]

    # Agar hozirda band bo‘lsa (ya’ni davom etayotgan bo‘lsa)
    if not lock.acquire(blocking=False):
        return False  # ishga tushmaydi

    def run():
        try:
            sync_status[sync_type] = True
            target_func()  # asosiy sinxron funksiya
        except Exception as e:
            handle_exception(e)
            print(f"[{sync_type}] Xato yuz berdi:", e)
        finally:
            sync_status[sync_type] = False
            lock.release()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return True
