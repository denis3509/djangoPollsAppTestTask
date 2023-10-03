from django.urls import path
from django.urls import path
from django.urls import include, path
from . import views

urlpatterns = [
    path("poll-list/", views.ListPolls.as_view()),
    path("question/", views.Question.as_view())
]