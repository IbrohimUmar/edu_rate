from django.urls import path, include
from .sync import setting_sync
urlpatterns = [
    path('sync', setting_sync, name='setting_sync'),
    path('user/', include("views.setting.user.urls")),
    # path('setting/', include("views.setting.urls")),
]
