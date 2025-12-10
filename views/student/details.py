from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from models.models.student_meta import StudentMeta
from models.models.user import User


@login_required(login_url='login')
def student_details(request, id):
    student = get_object_or_404(User, id=id, type='3')
    student_meta = StudentMeta.objects.filter(user=student)
    return render(request, "student/details.html", {
        'student': student,
        'student_meta': student_meta})



