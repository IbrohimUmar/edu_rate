from django.db import models
from .user import User


class ExportFile(models.Model):
    STATUS = [
        ('processing', 'Bajarilmoqda..'),
        ('done', 'Muvaffaqiyatli'),
        ('failed', 'Xatolik yuzaga keldi'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='processing')
    file = models.FileField(upload_to="exports/", null=True, blank=True)
    progress = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
