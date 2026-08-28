from django.db.models import Avg, Case, Count, FloatField, When
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.learning.models import Attempt


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
