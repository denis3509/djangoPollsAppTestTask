import copy

from rest_framework import serializers
from polls import models as mdl


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.Choice
        fields = ['question_id', 'choice_text', 'id']


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.Poll
        fields = ['id', 'title']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.Question
        fields = ['id', 'question_text', 'type', 'poll_id', 'poll', 'order', 'choice_set']

    poll = PollSerializer()
    choice_set = ChoiceSerializer(
        many=True,
        read_only=True,
    )


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.TestResult
        fields = ['id', 'poll', 'total_count', 'correct_count', 'started_at', 'finished_at']

    poll = PollSerializer(

    )
