from django.urls import path, include
from .views import AnswerSubmitView, ActiveAnswerListView

urlpatterns = [
    path('list', ActiveAnswerListView.as_view()),
    path('answer/submit', AnswerSubmitView.as_view()),
    # path('active/', ScheduleDetailByIdView.as_view()),
]
