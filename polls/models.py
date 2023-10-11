from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from pollsApp.models import BaseModel

User = get_user_model()


class Poll(BaseModel):
    """cant be edited after publishing"""
    title = models.TextField()
    published = models.BooleanField(default=False)

    def __str__(self):
        return f'Опрос "{self.title}"'


class Question(BaseModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "poll_id"],
                name="unique_order"
            ),
        ]

    SINGLE = 1
    MULTIPLE = 2
    QUESTION_TYPES = [
        (SINGLE, "Single"),
        (MULTIPLE, "Multiple"),
    ]
    question_text = models.TextField()
    type = models.IntegerField(
        choices=QUESTION_TYPES,
        default=SINGLE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField()

    def __str__(self):
        return f"Вопрос {self.id}. {self.question_text}"

    def is_single(self):
        return self.type == 1

    def is_multiple(self):
        return self.type == 2

    def correct_choices(self):
        choices = []
        for ch in self.choice_set.all():
            if ch.is_right:
                choices.append(ch)
        return choices




class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField()
    is_right = models.BooleanField(verbose_name="Правильный ответ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ответ на {self.question_id}: {self.choice_text}"


class TestResult(BaseModel):
    """user's test results: poll, start_date, finish_date..."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    current_question = models.IntegerField(null=True, default=0)
    correct_count = models.IntegerField(null=True, default=None)
    total_count = models.IntegerField(null=True, default=None)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TestAnswers(BaseModel):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
