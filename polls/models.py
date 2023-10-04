from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


from pollsApp.models import BaseModel

User = get_user_model()


class Poll(BaseModel):
    title = models.CharField(max_length=300)
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
    question_text = models.CharField(max_length=200)
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

    def is_valid(self):
        """raises exception if the question has incorrect choices"""
        total_count = 0
        true_count = 0
        for choice in self.choice_set.all():
            total_count += 1
            if choice.is_right:
                true_count += 1

        if total_count < 2:
            raise ValidationError(f"Мало ответов для {self.question_text}")

        if true_count == 0:
            raise ValidationError(f"Мало правильных ответов для {self.question_text}")

        if self.is_single():
            if true_count > 1:
                raise ValidationError(
                    f"Для данного типа вопросов допустим лишь один правильный ответ для {self.question_text}")

    def correct_choices(self):
        choices = []
        for ch in self.choice_set.all():
            if ch.is_right:
                choices.append(ch)
        return []



class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_right = models.BooleanField(verbose_name="Правильный ответ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ответ на {self.question_id}: {self.choice_text}"


# class PollsQuestions(BaseModel):
#     class Meta:
#         ordering = ['order_number']
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["question_id", "poll_id"],
#                 name="unique_questions"
#             ),
#             models.UniqueConstraint(
#                 fields=["order_number", "poll_id"],
#                 name="unique_order"
#             ),
#         ]
#
#     order_number = models.IntegerField()
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f'"{self.question.question_text}" для "{self.poll.title}"'


class UserTest(BaseModel):
    """user's test results: poll, start_date, finish_date..."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    current_question = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    total_questions = models.IntegerField(null=True)
    correct_answers = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class UserTestAnswers(BaseModel):
    user_test = models.ForeignKey(UserTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(null=True)
