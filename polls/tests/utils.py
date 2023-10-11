from datetime import datetime, timedelta
from typing import List

from django.contrib.auth import get_user_model

from pollsApp.testutils import BaseFaker
from polls import models as mdl

User = get_user_model()


class PollsFaker(BaseFaker):
    def question(self, poll: mdl.Poll,
                 question_type: int = None,
                 order: int = None,
                 choices: bool = False,
                 save: bool = True) -> mdl.Question:
        question = mdl.Question(
            poll=poll,
            question_text=self.sentence(),
            type=question_type or self.random.choice([1, 2]),
            order=order or 1,
        )
        if choices:
            pass
        if save:
            question.save()
        return question

    def question_bulk(self, n: int, poll: mdl.Poll):
        questions = [self.question(poll, order=i + 1, save=False) for i in range(n)]
        return mdl.Question.objects.bulk_create(questions)

    def poll(self, title: str = None, published: bool = None, save=True) -> mdl.Poll:
        if published is None:
            published = self.random.choice([False, True])
        poll = mdl.Poll(
            published=published,
            title=title or self.sentence()
        )
        if save:
            poll.save()
        return poll

    def choice(self, question: mdl.Question, choice_text: str = None,
               is_right: bool = None, save=True) -> mdl.Choice:
        if is_right is None:
            is_right = self.random.choice([False, True])
        choice = mdl.Choice(
            question=question,
            choice_text=choice_text or self.sentence(),
            is_right=is_right,
        )
        if save:
            choice.save()
        return choice

    def valid_choices(self, question: mdl.Question, save=True):
        choices = []
        choices.append(self.choice(question, is_right=True, save=False))

        if question.is_single():
            choices.append(self.choice(question, is_right=False, save=False))
            choices.append(self.choice(question, is_right=False, save=False))
            choices.append(self.choice(question, is_right=False, save=False))

        if question.is_multiple():
            choices.append(self.choice(question, is_right=True, save=False))
            choices.append(self.choice(question, is_right=False, save=False))
            choices.append(self.choice(question, is_right=False, save=False))

        if save:
            choices = mdl.Choice.objects.bulk_create(choices)
        return choices

    def valid_choice_bulk(self, questions: List[mdl.Question]):
        choices = []
        for que in questions:
            choices.extend(self.valid_choices(que, save=False))
        return mdl.Choice.objects.bulk_create(choices)

    def test_result(self, user: User, poll: mdl.Poll,
                    current_question: int = None,
                    started: bool = False, finished: bool = False,
                    test_answers=False,
                    save=True):
        test_result = mdl.TestResult(
            user=user,
            poll=poll,
            current_question=0,
            total_count=poll.question_set.count()
        )
        if started:
            test_result.started_at = datetime.now() - timedelta(hours=1)
            test_result.current_question = current_question or 1
        if finished:
            test_result.finished_at = datetime.now()
            test_result.current_question = None
        if save:
            test_result.save()

        return test_result

    def test_answers(self, test_result, choices, save=True):
        answers = []
        for choice in choices:
            answer = mdl.TestAnswers(test_result=test_result,
                                     choice=choice)
            answers.append(answer)
        return mdl.TestAnswers.objects.bulk_create(answers)
