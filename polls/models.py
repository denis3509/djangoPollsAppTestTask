from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Question(models.Model):
    SINGLE = 1
    MULTIPLE = 2
    QUESTION_TYPES = [
        (SINGLE, "Single"),
        (MULTIPLE, "Multiple"),
    ]
    question_text = models.CharField(max_length=200)
    type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPES,
        default=SINGLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_right = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Poll(models.Model):
    title = models.CharField(max_length=300)
    questions = models.ManyToManyField(
        Question,
        through='PollsQuestions',
        through_fields=('poll', 'question'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PollsQuestions(models.Model):
    class Meta:
        ordering = ["order_number"]
    order_number = models.IntegerField()
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class UserTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    current_question = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserTestAnswers(models.Model):
    test = models.ForeignKey(UserTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
