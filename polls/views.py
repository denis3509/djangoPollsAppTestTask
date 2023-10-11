from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.core.exceptions import ValidationError
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from rest_framework_simplejwt import authentication as jwt_auth

from polls import models as mdl
from polls import service
from polls.serializers import QuestionSerializer
from polls import serializers as sers


class ListPolls(APIView):
    authentication_classes = [jwt_auth.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all available polls.
        """
        polls = mdl.Poll.objects.filter(published=True)
        polls_ser = sers.PollSerializer(polls, many=True)
        return Response({'polls': polls_ser.data})


class TestResultList(APIView):
    authentication_classes = [jwt_auth.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
         user's tests results
        """
        tests = mdl.TestResult.objects.filter(started_at__isnull=False,
                                              finished_at__isnull=False,
                                              user=request.user).order_by("-finished_at")
        ser = sers.TestResultSerializer(tests, many=True)
        return Response({'results': ser.data})


class TestResult(APIView):
    authentication_classes = [jwt_auth.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        test_result = mdl.TestResult.objects.get(
            id=request.query_params["test_result_id"],
            user=request.user)

        ser = sers.TestResultSerializer(test_result)
        return Response({'test_result': ser.data})


@api_view(['POST'])
@authentication_classes([jwt_auth.JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def start_test(request):
    poll_id = request.data["poll_id"]
    poll = mdl.Poll.objects.get(id=poll_id)
    try:
        service.start_test(request.user, poll)
        return Response(status=200)
    except ValidationError:
        return Response(status=400)



class TestAnswer(APIView):
    authentication_classes = [jwt_auth.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        user_choices_ids = request.data["user_choices_ids"]
        question = mdl.Question.objects.get(id=request.data["question_id"])
        user_choices = mdl.Choice.objects.filter(id__in=user_choices_ids)
        test_result = service.answer_question(request.user, question, user_choices)
        if test_result.current_question is None:
            service.finish_test(request.user)
        return Response(status=200)


class Question(APIView):
    authentication_classes = [jwt_auth.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        question = service.get_current_question(request.user)
        if question:
            title = question.poll.title
            total_questions = question.poll.question_set.count()
            question_ser = QuestionSerializer(question)
            test_result = service.get_incomplete_test(request.user)

            result = {'question': dict(**dict(question_ser.data),
                                       poll_title=title,
                                       test_result_id=test_result.id,
                                       total_questions=total_questions)}
            return Response(result)
        else:
            return Response({'question': None})
