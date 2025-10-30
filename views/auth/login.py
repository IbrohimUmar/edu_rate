from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.shortcuts import render, redirect


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
