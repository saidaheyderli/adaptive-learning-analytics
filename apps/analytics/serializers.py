from rest_framework import serializers

from apps.learning.models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)

    class Meta:
        model = Recommendation
        fields = (
            'id', 'topic', 'topic_name', 'accuracy_at_generation',
            'explanation', 'practice_prompt', 'practice_choices', 'created_at',
        )
