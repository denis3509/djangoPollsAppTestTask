from typing import List

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from pollsApp import utils
from . import models as mdl

User = get_user_model()


def get_incomplete_test(user):
    incomplete_test = mdl.UserTest.objects \
        .filter(Q(started_at__isnull=True) | Q(finished_at__isnull=True), user=user).first()
    return incomplete_test


def create_user_test(user: User, poll):
    incomplete_test = get_incomplete_test(user)
    if incomplete_test is not None:
        raise ValidationError(f"user already started test {incomplete_test.poll.title}")
    user_test = mdl.UserTest.objects.create(poll=poll,
                                            user=user,
                                            current_question=1,
                                            total_questions=poll.question_set.count())
    return user_test


def answer_question(user_test: mdl.UserTest, question: mdl.Question, user_choices: List[mdl.Choice]):
    answers = []
    if len(user_choices):
        ValidationError("empty choices")
    for choice in user_choices:
        ans = mdl.UserTestAnswers(
            question=question,
            choice=choice,
            user_test=user_test,
        )
        answers.append(ans)

    with transaction.atomic():
        mdl.UserTestAnswers.objects.bulk_create(answers)
        user_test.current_question += 1
        user_test.save()



def get_current_question(user):
    incomplete_test = mdl.UserTest.objects \
        .filter(Q(started_at__isnull=True) | Q(finished_at__isnull=True), user=user).first()
    try:
        que = mdl.Question.objects.get(poll=incomplete_test.poll,
                                       order=incomplete_test.current_question)
        return que
    except mdl.Question.DoesNotExist:
        return None


def finish_test(user_test: mdl.UserTest):
    calc_results(user_test)
    return dict(total=user_test.total_questions,
                correct=user_test.correct_answers,
                percentage=user_test.correct_answers / user_test.total_questions
                )

def calc_results(user_test: mdl.UserTest):
    questions = user_test.poll.question_set.all().order_by("order")
    correct_count = 0
    for que in questions:
        # TODO optimization
        user_answers = mdl.UserTestAnswers.objects.filter(user_test=user_test,
                                                          question=que)
        if set(user_answers) == set(que.correct_choices()):
            correct_count = +1
    total = user_test.poll.question_set.all().count()
    user_test.total_questions = total
    user_test.correct_answers = correct_count
    user_test.save()


def validate_poll(poll: mdl.Poll):
    prev_order = 0
    for que in poll.question_set.select_related("choices_set").all().order_by("order"):
        que.is_valid()
        if not que.order == prev_order + 1:
            raise ValidationError(f"incorrect order values {que}")
        prev_order = prev_order + 1
