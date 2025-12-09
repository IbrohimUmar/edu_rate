import io, datetime
from django.utils import timezone
from django.core.paginator import Paginator
from models.models.export_file import ExportFile
from services.export_file.schedule.format1.data_format import export_file_schedule_format1_data_format
from services.export_file.schedule.format1.export_excel_ram import export_file_schedule_format1_excel_ram



def export_file_schedule_format1_manager(schedules, survey, user):
    PAGE_SIZE = 100  # her sayfada kaç schedule işlenecek
    export_obj = ExportFile.objects.create(
        user=user,
        name=f"{survey.education_type.name} - So'rovnomalar - soni:{schedules.count()} - sana:{timezone.now().strftime('%Y%m%d-%H:%M%S')}",
        status="processing",
        progress=0
    )
    paginator = Paginator(schedules, PAGE_SIZE)

    total_pages = paginator.num_pages
    for page_number in range(1, total_pages + 1):
        page_schedules = paginator.page(page_number).object_list
        data = export_file_schedule_format1_data_format(page_schedules, survey)

        # Fonksiyonumuz RAM'de workbook açıp ekleyecek ve export_file'a kaydedecek
        export_file_schedule_format1_excel_ram(data, survey, export_file=export_obj)
        # Progress güncelle
        export_obj.progress = int(page_number / total_pages * 100)
        export_obj.save()

    export_obj.completed_at = datetime.datetime.now()
    export_obj.status = "done"
    export_obj.save()