import copy

from rest_framework import serializers
from polls import models as mdl


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.Choice
        fields = ['question_id', 'choice_text', 'id']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.Question
        fields = ['id', 'question_text', 'type', 'poll_id', 'order', 'choice_set']

    choice_set = ChoiceSerializer(
        many=True,
        read_only=True,
    )


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.Question
        fields = ['id', 'title']

    choice_set = ChoiceSerializer(
        many=True,
        read_only=True,
    )
