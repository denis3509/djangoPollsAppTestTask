from datetime import datetime
from typing import List

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from . import models as mdl

User = get_user_model()


def validate_question(question):
    """raises exception if the question has incorrect choices"""
    total_count = 0
    true_count = 0
    for choice in question.choice_set.all():
        total_count += 1
        if choice.is_right:
            true_count += 1

    if total_count < 2:
        raise ValidationError(f"Мало ответов для {question.question_text}")

    if true_count == 0:
        raise ValidationError(f"Мало правильных ответов для {question.question_text}")

    if question.is_single():
        if true_count > 1:
            raise ValidationError(
                f"Для данного типа вопросов допустим лишь один правильный ответ для {question.question_text}")


def get_incomplete_test(user):
    try:
        incomplete_test = mdl.TestResult.objects \
            .get(started_at__isnull=False, finished_at__isnull=True, user=user)
        return incomplete_test
    except mdl.TestResult.DoesNotExist:
        return None


def start_test(user: User, poll: mdl.Poll) -> mdl.TestResult:
    """creates test_result and start a test for user"""
    if not poll.published:
        raise ValidationError("poll unavailable now")
    incomplete_test = get_incomplete_test(user)
    if incomplete_test is not None:
        raise ValidationError(f"user already started test {incomplete_test.poll.title}")
    total = poll.question_set.count()
    test_rest = mdl.TestResult.objects.create(poll=poll,
                                              user=user,
                                              total_count=total,
                                              current_question=1,
                                              started_at=datetime.now(),
                                              )
    return test_rest


def answer_question(user, question: mdl.Question, user_choices: List[mdl.Choice]) -> mdl.TestResult:
    if len(user_choices) == 0:
        raise ValidationError("empty choices")

    test_result = get_incomplete_test(user)
    if not test_result:
        raise ValidationError("No active tests found")
    answers = []
    for choice in user_choices:
        assert choice.question == question
        ans = mdl.TestAnswers(
            choice=choice,
            test_result=test_result,
        )
        answers.append(ans)

    with transaction.atomic():
        mdl.TestAnswers.objects.bulk_create(answers)
        if test_result.current_question + 1 <= test_result.poll.question_set.count():
            test_result.current_question += 1
        else:
            test_result.current_question = None
        test_result.save()
    return test_result


def get_current_question(user):
    incomplete_test = get_incomplete_test(user)
    if incomplete_test is None:
        return None
    try:
        que = mdl.Question.objects.get(poll=incomplete_test.poll,
                                       order=incomplete_test.current_question)
        return que
    except mdl.Question.DoesNotExist:
        return None


def finish_test(user) -> mdl.TestResult:
    test_result = get_incomplete_test(user)
    if not test_result:
        raise ValidationError("No active tests found")

    if test_result.current_question is not None:
        raise ValidationError(f"Test {test_result.poll.title} has not been completed")
    correct = count_correct_answers(test_result)

    test_result.finished_at = datetime.now()
    test_result.correct_count = correct
    test_result.save()

    return test_result


def count_correct_answers(test_result: mdl.TestResult):
    questions = test_result.poll.question_set.all().order_by("order")

    correct_count = 0
    for que in questions:
        # TODO optimization
        user_answers = mdl.TestAnswers.objects.filter(test_result=test_result,
                                                      choice__question=que)
        user_choices = [ans.choice for ans in user_answers]
        if set(user_choices) == set(que.correct_choices()):
            correct_count += 1
    return correct_count


def validate_poll(poll: mdl.Poll):
    prev_order = 0
    for que in poll.question_set.all() \
            .prefetch_related("choice_set").all().order_by("order"):
        validate_question(que)
        if not que.order == prev_order + 1:
            raise ValidationError(f"incorrect order values {que}")
        prev_order = prev_order + 1
