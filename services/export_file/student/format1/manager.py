from django.core.paginator import Paginator
from django.utils import timezone
import datetime

from models.models.export_file import ExportFile
from services.export_file.student.format1.data_format import export_students_data_format
from services.export_file.student.format1.export_excel_ram import export_students_excel_ram


def export_students_manager(students_qs, user):
    PAGE_SIZE = 500

    export_obj = ExportFile.objects.create(
        user=user,
        name=f"Talabalar - soni:{students_qs.count()} - sana:{timezone.now().strftime('%Y%m%d-%H%M%S')}",
        status="processing",
        progress=0
    )

    paginator = Paginator(students_qs, PAGE_SIZE)
    total_pages = paginator.num_pages

    try:
        for page_number in range(1, total_pages + 1):
            page_students = paginator.page(page_number).object_list

            data = export_students_data_format(page_students)
            export_students_excel_ram(data, export_obj)

            export_obj.progress = int(page_number / total_pages * 100)
            export_obj.save(update_fields=["progress"])

        export_obj.status = "done"
        export_obj.completed_at = timezone.now()
        export_obj.progress = 100
        export_obj.save()

    except Exception as e:
        export_obj.status = "failed"
        export_obj.save()
        raise e
