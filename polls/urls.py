from django.urls import path
from django.urls import path
from django.urls import include, path
from . import views

urlpatterns = [
    path("poll-list/", views.ListPolls.as_view()),
    path("question/", views.Question.as_view()),
    path("test-result/", views.TestResult.as_view()),
    path("test-result-list/", views.TestResultList.as_view()),
    path("start-test/", views.start_test),
    path("test-answer/", views.TestAnswer.as_view()),
]