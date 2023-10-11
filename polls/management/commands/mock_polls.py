from django.core.management.base import BaseCommand, CommandError
from polls.models import Question as Poll
from polls.tests.utils import PollsFaker


class Command(BaseCommand):
    help = "generates mock data"

    for _ in range(20):
        f = PollsFaker()
        poll = f.poll()
        ques = f.question_bulk(f.random.randrange(3, 7), poll)
        f.valid_choice_bulk(ques)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Successfully mocked polls')
        )
