from django.db.models.signals import post_delete
from django.dispatch import receiver
from models.models.export_file import ExportFile

@receiver(post_delete, sender=ExportFile)
def delete_file_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(False)
