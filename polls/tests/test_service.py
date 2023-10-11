from unittest.mock import patch

from django.test import TestCase

from django.core.exceptions import ValidationError
from polls import models as mdl
from .utils import PollsFaker
from polls import service as srv


class Test(TestCase):

    def test_validate_question(self):
        f = PollsFaker()
        poll = f.poll(published=True)
        question = f.question(poll, question_type=1)
        with self.assertRaises(ValidationError):
            srv.validate_question(question)

        choice = f.choice(question, is_right=True)
        with self.assertRaises(ValidationError):
            srv.validate_question(question)

        f.choice(question, is_right=False)
        srv.validate_question(question)

        choice.is_right = False
        choice.save()
        with self.assertRaises(ValidationError):
            srv.validate_question(question)

        question = f.question(poll, question_type=2, order=2)
        f.choice(question, is_right=True)
        f.choice(question, is_right=False)
        f.choice(question, is_right=True)
        srv.validate_question(question)

    def test_start_test(self):
        f = PollsFaker()
        poll = f.poll(published=False)
        user = f.user()
        with self.assertRaises(ValidationError):
            srv.start_test(user, poll)

        poll.published = True
        poll.save()

        srv.start_test(user, poll)

        with self.assertRaises(ValidationError):
            srv.start_test(user, poll)

    def test_get_incomplete_test(self):
        f = PollsFaker()
        poll = f.poll(published=True)
        poll2 = f.poll(published=True)
        f.question_bulk(15, poll)
        f.question_bulk(15, poll2)
        user = f.user()
        test_result1 = f.test_result(user, poll, current_question=15, started=True, finished=False)
        test_result2 = f.test_result(user, poll, current_question=15, started=True, finished=True)

        incomplete_test = srv.get_incomplete_test(user)
        self.assertEqual(test_result1,
                         incomplete_test)

    def test_get_current_question(self):
        f = PollsFaker()
        poll = f.poll(published=True)
        f.question_bulk(15, poll)
        user = f.user()
        f.test_result(user, poll, current_question=15, started=True, finished=False)
        question = srv.get_current_question(user)
        self.assertEqual(question.order, 15)

    def test_answer_question(self):
        f = PollsFaker()
        poll = f.poll(published=True)
        question1 = f.question(poll, question_type=1, order=1)
        question2 = f.question(poll, question_type=1, order=2)
        choice1 = f.choice(question1)
        choice2 = f.choice(question2)
        user = f.user()

        with self.assertRaises(ValidationError):
            srv.answer_question(user, question1, [choice1])

        test_result = f.test_result(user, poll, started=True, finished=False)
        with self.assertRaises(AssertionError):
            srv.answer_question(user, question1, [choice1, choice2])

        srv.answer_question(user, question1, [choice1])

    @patch("polls.service.count_correct_answers", return_value=1)
    def test_finish_test(self, m1):
        f = PollsFaker()
        poll = f.poll(published=True)
        question1 = f.question(poll, question_type=1, order=1)
        question2 = f.question(poll, question_type=1, order=2)
        user = f.user()
        test_result = f.test_result(user, poll, started=True,
                                    current_question=1,
                                    finished=True)
        with self.assertRaises(ValidationError) as e:
            srv.finish_test(user)
            self.assertEqual(e, "No active tests found")

        test_result = f.test_result(user, poll, started=True,
                                    current_question=2,
                                    finished=False)

        with self.assertRaises(ValidationError) as e:
            srv.finish_test(user)
            self.assertEqual(e, f"Test {test_result.poll.title} has not been completed")

        test_result.current_question = None
        test_result.save()

        res = srv.finish_test(user)
        self.assertEqual(res.correct_count, 1)
        self.assertEqual(res.total_count, 2)

    @patch("polls.service.validate_question")
    def test_validate_poll(self, m1):
        f = PollsFaker()
        poll = f.poll(published=True)
        question1 = f.question(poll, question_type=1, order=1)

        question3 = f.question(poll, question_type=1, order=3)

        with self.assertRaises(ValidationError):
            srv.validate_poll(poll)

        question3 = f.question(poll, question_type=1, order=2)
        srv.validate_poll(poll)

    def test_count_correct_answers(self):
        f = PollsFaker()
        poll = f.poll(published=True)
        question1 = f.question(poll, question_type=1, order=1)
        question2 = f.question(poll, question_type=2, order=2)
        choices1 = f.valid_choices(question1)
        choices2 = f.valid_choices(question2)
        user = f.user()
        test_result = f.test_result(user, poll, started=True,
                                    finished=True)
        f.test_answers(test_result, [choices1[1], choices2[3]])
        res = srv.count_correct_answers(test_result)
        self.assertEqual(res, 0)

    def test_count_correct_answers_2(self):
        f = PollsFaker()
        poll = f.poll(published=True)
        question1 = f.question(poll, question_type=1, order=1)
        question2 = f.question(poll, question_type=2, order=2)
        choices1 = f.valid_choices(question1)
        choices2 = f.valid_choices(question2)
        user = f.user()
        test_result = f.test_result(user, poll, started=True,
                                    finished=True)
        f.test_answers(test_result, [choices1[0], choices2[0], choices2[1]])
        res = srv.count_correct_answers(test_result)
        self.assertEqual(res, 2)
