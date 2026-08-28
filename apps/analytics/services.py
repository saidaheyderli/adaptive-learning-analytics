"""
Business logic for weakness detection and recommendation generation.
Kept separate from views so it's independently testable and reusable
(e.g. from a future management command or Celery task).
"""

from django.conf import settings
from django.db.models import Avg, Case, Count, FloatField, When

from apps.learning.models import Attempt, Recommendation, Topic

from .gemini_client import GeminiRecommendationError, generate_recommendation


def get_weak_topics(student, threshold=None, min_attempts=None):
    """
    Return a list of {topic, accuracy_percent, total_attempts} dicts for
    topics where the student's accuracy is below the weakness threshold,
    based on at least `min_attempts` attempts.
    """
    threshold = threshold if threshold is not None else settings.WEAKNESS_THRESHOLD_PERCENT
    min_attempts = min_attempts if min_attempts is not None else settings.WEAKNESS_MIN_ATTEMPTS

    stats = (
        Attempt.objects.filter(student=student)
        .values('question__topic')
        .annotate(
            total_attempts=Count('id'),
            accuracy=Avg(
                Case(When(is_correct=True, then=1), default=0, output_field=FloatField())
            ),
        )
        .filter(total_attempts__gte=min_attempts)
    )

    weak = []
    for row in stats:
        accuracy_percent = round((row['accuracy'] or 0) * 100, 1)
        if accuracy_percent < threshold:
            weak.append({
                'topic_id': row['question__topic'],
                'accuracy_percent': accuracy_percent,
                'total_attempts': row['total_attempts'],
            })
    return weak


def get_or_create_recommendation(student, topic_id, accuracy_percent):
    """
    Return a cached Recommendation for this student/topic if one already
    exists at the same (or worse) accuracy level; otherwise call Gemini
    to generate a fresh one and store it.
    """
    existing = (
        Recommendation.objects.filter(student=student, topic_id=topic_id)
        .order_by('-created_at')
        .first()
    )
    if existing and existing.accuracy_at_generation <= accuracy_percent:
        return existing, False

    topic = Topic.objects.get(id=topic_id)
    recent_prompts = list(
        Attempt.objects.filter(student=student, question__topic_id=topic_id)
        .values_list('question__prompt', flat=True)
        .distinct()[:5]
    )

    data = generate_recommendation(topic.name, accuracy_percent, recent_prompts)

    recommendation = Recommendation.objects.create(
        student=student,
        topic=topic,
        accuracy_at_generation=accuracy_percent,
        explanation=data['explanation'],
        practice_prompt=data['practice_prompt'],
        practice_choices=data['practice_choices'],
    )
    return recommendation, True
