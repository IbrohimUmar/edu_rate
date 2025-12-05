from django.urls import path, include
from views.auth.login import login_user, logout_user
from .callback_login import auth_callback_login

urlpatterns = [
    path('login', login_user, name="login"),
    path('logout', logout_user, name='logout'),
    path('callback-login', auth_callback_login, name='auth_callback_login'),
]