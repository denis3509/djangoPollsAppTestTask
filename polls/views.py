from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from polls import models as mdl
from polls import service
from polls.serializers import QuestionSerializer
from polls import serializers as sers


class ListPolls(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all available polls.
        """
        polls = mdl.Poll.objects.filter(published=True)
        polls_ser = sers.PollSerializer(polls, many=True)
        return Response(polls_ser.data)


class ListUserTest(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all available polls.
        """
        tests = mdl.UserTest.objects.filter(started_at__isnull=False,
                                            finished_at__isnull=False,
                                            user=request.user)
        polls_ser = sers.UserTestSerializer(tests, many=True)
        return Response(polls_ser.data)


class UserTest(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        poll_id = request.data["poll_id"]
        poll = mdl.Poll.objects.get(poll_id)
        user_test = service.create_user_test(request.user, poll)
        return Response(user_test)

    def get(self, request, format=None):
        user_test_id = request.data["user_test_id"]
        user_test = mdl.UserTest.objects.get(user_test_id)
        return Response(user_test)


class UserTestAnswer(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        user_test_id = request.data["user_test_id"]
        user_choices_ids = request.data["user_choices_ids"]
        question = request.data["question_id"]

        user_test = mdl.UserTest.objects.get(user_test_id)
        user_choices = mdl.Choice.objects.filter(id__in=user_choices_ids)
        service.answer_question(user_test, question, user_choices)

        return Response(user_test)


class Question(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user_test_id = request.query_params["user_test_id"]

        user_test = mdl.UserTest.objects.get(user_test_id)
        question = service.get_current_question(user_test)

        question_ser = QuestionSerializer(question).data
        return Response(dict(question_ser))
