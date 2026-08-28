from django.db.models import Avg, Case, Count, FloatField, When
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.learning.models import Attempt

from .gemini_client import GeminiRecommendationError
from .serializers import RecommendationSerializer
from .services import get_or_create_recommendation, get_weak_topics


class TopicAccuracyView(APIView):
    """
    Per-topic accuracy for the current student (or, for instructors,
    class-wide per-topic accuracy). This is the basic MVP analytics
    endpoint — no ML yet, just aggregated correctness percentages.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Attempt.objects.select_related('question__topic')
        if not user.is_instructor:
            qs = qs.filter(student=user)

        stats = (
            qs.values('question__topic__id', 'question__topic__name')
            .annotate(
                total_attempts=Count('id'),
                accuracy=Avg(
                    Case(
                        When(is_correct=True, then=1),
                        default=0,
                        output_field=FloatField(),
                    )
                ),
            )
            .order_by('question__topic__name')
        )

        results = [
            {
                'topic_id': row['question__topic__id'],
                'topic_name': row['question__topic__name'],
                'total_attempts': row['total_attempts'],
                'accuracy_percent': round((row['accuracy'] or 0) * 100, 1),
            }
            for row in stats
        ]
        return Response(results)


class RecommendationsView(APIView):
    """
    For the current student: detect weak topics (accuracy below
    WEAKNESS_THRESHOLD_PERCENT with at least WEAKNESS_MIN_ATTEMPTS
    attempts) and return an AI-generated explanation + practice question
    for each. Recommendations are cached per student/topic and only
    regenerated if accuracy has dropped further since the last one.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user
        weak_topics = get_weak_topics(student)

        results = []
        errors = []
        for weak in weak_topics:
            try:
                recommendation, _created = get_or_create_recommendation(
                    student, weak['topic_id'], weak['accuracy_percent']
                )
                results.append(RecommendationSerializer(recommendation).data)
            except GeminiRecommendationError as exc:
                errors.append({'topic_id': weak['topic_id'], 'error': str(exc)})

        payload = {'recommendations': results}
        if errors:
            payload['generation_errors'] = errors
        return Response(payload)
