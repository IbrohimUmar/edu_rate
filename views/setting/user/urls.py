from django.urls import path, include
from .list import setting_user_list

urlpatterns = [
    path('list/', setting_user_list, name='setting_user_list'),
    # path('auth/', include("views.auth.urls")),
    # path('setting/', include("views.setting.urls")),
]
