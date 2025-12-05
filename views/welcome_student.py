from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models.models.user import User
from models.models.student_meta import StudentMeta

@login_required(login_url='login')
def welcome_student(request):
    student_meta = StudentMeta.objects.filter(user_id=request.user.id)
    return render(request, 'welcome_student.html', {
        "student_meta":student_meta})