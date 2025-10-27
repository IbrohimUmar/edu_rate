from django.urls import path, include
from .sync import setting_sync
urlpatterns = [
    path('sync', setting_sync, name='setting_sync'),
    # path('auth/', include("views.auth.urls")),
    # path('setting/', include("views.setting.urls")),
]
