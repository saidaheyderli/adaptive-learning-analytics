from rest_framework import serializers

from .models import AnswerChoice, Attempt, Question, Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'name', 'slug', 'description', 'created_at')


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ('id', 'text')  # is_correct intentionally hidden from students


class AnswerChoiceWriteSerializer(serializers.ModelSerializer):
    """Used by instructors, where is_correct must be settable."""

    class Meta:
        model = AnswerChoice
        fields = ('id', 'text', 'is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())

    class Meta:
        model = Question
        fields = ('id', 'topic', 'prompt', 'difficulty', 'choices', 'created_at')
        read_only_fields = ('created_at',)


class AttemptSubmitSerializer(serializers.ModelSerializer):
    """Used when a student submits an answer. student/is_correct are derived, not sent by the client."""

    class Meta:
        model = Attempt
        fields = ('id', 'question', 'selected_choice', 'time_taken_seconds', 'submitted_at')
        read_only_fields = ('id', 'submitted_at')

    def validate(self, attrs):
        question = attrs['question']
        selected_choice = attrs.get('selected_choice')
        if selected_choice and selected_choice.question_id != question.id:
            raise serializers.ValidationError(
                'selected_choice does not belong to the given question.'
            )
        return attrs

    def create(self, validated_data):
        selected_choice = validated_data.get('selected_choice')
        validated_data['is_correct'] = bool(selected_choice and selected_choice.is_correct)
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class AttemptReadSerializer(serializers.ModelSerializer):
    topic = serializers.CharField(source='question.topic.name', read_only=True)

    class Meta:
        model = Attempt
        fields = (
            'id', 'question', 'topic', 'selected_choice',
            'is_correct', 'time_taken_seconds', 'submitted_at',
        )
