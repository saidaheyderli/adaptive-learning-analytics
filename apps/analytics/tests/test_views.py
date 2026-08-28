from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.learning.tests.factories import AttemptFactory, QuestionFactory, TopicFactory, UserFactory

pytestmark = pytest.mark.django_db

FAKE_GEMINI_RESPONSE = {
    'explanation': 'Focus on identifying the base case first.',
    'practice_prompt': 'What terminates a recursive function?',
    'practice_choices': [
        {'text': 'The base case', 'is_correct': True},
        {'text': 'A print statement', 'is_correct': False},
    ],
}


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestRecommendationsView:
    @patch('apps.analytics.services.generate_recommendation')
    def test_returns_recommendation_for_weak_topic(self, mock_generate):
        mock_generate.return_value = FAKE_GEMINI_RESPONSE
        student = UserFactory()
        topic = TopicFactory()
        for is_correct in [True, False, False, False]:
            question = QuestionFactory(topic=topic)
            AttemptFactory(student=student, question=question, is_correct=is_correct)

        response = auth_client(student).get('/api/analytics/recommendations/')

        assert response.status_code == 200
        assert len(response.data['recommendations']) == 1
        assert response.data['recommendations'][0]['topic_name'] == topic.name
        assert response.data['recommendations'][0]['explanation'] == FAKE_GEMINI_RESPONSE['explanation']

    def test_returns_empty_list_when_no_weak_topics(self):
        student = UserFactory()
        topic = TopicFactory()
        for is_correct in [True, True, True, True]:
            question = QuestionFactory(topic=topic)
            AttemptFactory(student=student, question=question, is_correct=is_correct)

        response = auth_client(student).get('/api/analytics/recommendations/')

        assert response.status_code == 200
        assert response.data['recommendations'] == []

    def test_requires_authentication(self):
        client = APIClient()
        response = client.get('/api/analytics/recommendations/')
        assert response.status_code == 401
