from unittest.mock import patch

import pytest

from apps.analytics.gemini_client import GeminiRecommendationError
from apps.analytics.services import get_or_create_recommendation, get_weak_topics
from apps.learning.models import Recommendation
from apps.learning.tests.factories import AnswerChoiceFactory, AttemptFactory, QuestionFactory, TopicFactory, UserFactory

pytestmark = pytest.mark.django_db

FAKE_GEMINI_RESPONSE = {
    'explanation': 'You seem to be mixing up base cases with recursive cases.',
    'practice_prompt': 'Which of these is a valid base case for factorial(n)?',
    'practice_choices': [
        {'text': 'n == 0', 'is_correct': True},
        {'text': 'n == n', 'is_correct': False},
        {'text': 'n > 0', 'is_correct': False},
    ],
}


def _make_attempt(student, topic, is_correct):
    question = QuestionFactory(topic=topic)
    AttemptFactory(student=student, question=question, is_correct=is_correct)


class TestGetWeakTopics:
    def test_topic_below_threshold_is_flagged(self):
        student = UserFactory()
        topic = TopicFactory()
        # 1 correct, 3 incorrect => 25% accuracy, 4 attempts >= min_attempts
        for is_correct in [True, False, False, False]:
            _make_attempt(student, topic, is_correct)

        weak = get_weak_topics(student, threshold=50, min_attempts=3)

        assert len(weak) == 1
        assert weak[0]['topic_id'] == topic.id
        assert weak[0]['accuracy_percent'] == 25.0

    def test_topic_above_threshold_is_not_flagged(self):
        student = UserFactory()
        topic = TopicFactory()
        for is_correct in [True, True, True, False]:
            _make_attempt(student, topic, is_correct)

        weak = get_weak_topics(student, threshold=50, min_attempts=3)
        assert weak == []

    def test_topic_below_min_attempts_is_not_flagged(self):
        student = UserFactory()
        topic = TopicFactory()
        # Only 2 attempts, both wrong — 0% accuracy but below min_attempts
        for is_correct in [False, False]:
            _make_attempt(student, topic, is_correct)

        weak = get_weak_topics(student, threshold=50, min_attempts=3)
        assert weak == []


class TestGetOrCreateRecommendation:
    @patch('apps.analytics.services.generate_recommendation')
    def test_creates_new_recommendation_when_none_exists(self, mock_generate):
        mock_generate.return_value = FAKE_GEMINI_RESPONSE
        student = UserFactory()
        topic = TopicFactory()
        QuestionFactory(topic=topic)

        recommendation, created = get_or_create_recommendation(student, topic.id, 25.0)

        assert created is True
        assert recommendation.explanation == FAKE_GEMINI_RESPONSE['explanation']
        assert Recommendation.objects.count() == 1
        mock_generate.assert_called_once()

    @patch('apps.analytics.services.generate_recommendation')
    def test_reuses_cached_recommendation_when_accuracy_not_worse(self, mock_generate):
        mock_generate.return_value = FAKE_GEMINI_RESPONSE
        student = UserFactory()
        topic = TopicFactory()
        QuestionFactory(topic=topic)

        first, created_first = get_or_create_recommendation(student, topic.id, 25.0)
        second, created_second = get_or_create_recommendation(student, topic.id, 30.0)

        assert created_first is True
        assert created_second is False
        assert first.id == second.id
        mock_generate.assert_called_once()  # not called again

    @patch('apps.analytics.services.generate_recommendation')
    def test_regenerates_when_accuracy_dropped_further(self, mock_generate):
        mock_generate.return_value = FAKE_GEMINI_RESPONSE
        student = UserFactory()
        topic = TopicFactory()
        QuestionFactory(topic=topic)

        get_or_create_recommendation(student, topic.id, 40.0)
        _, created_second = get_or_create_recommendation(student, topic.id, 20.0)

        assert created_second is True
        assert mock_generate.call_count == 2

    @patch('apps.analytics.services.generate_recommendation')
    def test_propagates_gemini_error(self, mock_generate):
        mock_generate.side_effect = GeminiRecommendationError('API unavailable')
        student = UserFactory()
        topic = TopicFactory()
        QuestionFactory(topic=topic)

        with pytest.raises(GeminiRecommendationError):
            get_or_create_recommendation(student, topic.id, 25.0)
