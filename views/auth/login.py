import datetime

from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.shortcuts import render, redirect

from config.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHORIZE_URL, TOKEN_URL, RESOURCE_OWNER_URL
from services.notification import send_message
from views.auth.client import oAuth2Client


def logout_user(request):
    logout(request)
    return redirect('login')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def login_user(request):
    if request.GET.get("from_hemis", None):
        client = oAuth2Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            authorize_url=AUTHORIZE_URL,
            token_url=TOKEN_URL,
            resource_owner_url=RESOURCE_OWNER_URL
        )
        chat_id = request.GET.get("chat_id", None)
        if not chat_id:
            messages.error(request, "1 Sizda xatolik chat id mavjud emas")
            return redirect('login')

        request.session['chat_id'] = chat_id
        authorization_url = client.get_authorization_url()
        return redirect(authorization_url)


    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Xush kelibsiz')
            return redirect('home')
        else:
            return render(request, 'auth/login.html',
                          {"email": request.POST['email'], 'password': request.POST['password'],
                           'messages_error': "Login yoki parol not'g'ri iltimos qayta urinib ko'ring."})
    return render(request, 'auth/login.html')
