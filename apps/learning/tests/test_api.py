import pytest
from rest_framework.test import APIClient

from apps.learning.tests.factories import (
    AnswerChoiceFactory,
    InstructorFactory,
    QuestionFactory,
    TopicFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestTopicPermissions:
    def test_student_cannot_create_topic(self):
        student = UserFactory()
        client = auth_client(student)
        response = client.post('/api/topics/', {'name': 'New Topic', 'slug': 'new-topic'})
        assert response.status_code == 403

    def test_instructor_can_create_topic(self):
        instructor = InstructorFactory()
        client = auth_client(instructor)
        response = client.post('/api/topics/', {'name': 'New Topic', 'slug': 'new-topic'})
        assert response.status_code == 201

    def test_anyone_authenticated_can_list_topics(self):
        TopicFactory()
        student = UserFactory()
        client = auth_client(student)
        response = client.get('/api/topics/')
        assert response.status_code == 200


class TestAttemptSubmission:
    def test_attempt_marks_correct_when_correct_choice_selected(self):
        student = UserFactory()
        question = QuestionFactory()
        correct_choice = AnswerChoiceFactory(question=question, is_correct=True)
        client = auth_client(student)

        response = client.post('/api/attempts/', {
            'question': question.id,
            'selected_choice': correct_choice.id,
            'time_taken_seconds': 5,
        })

        assert response.status_code == 201
        assert response.data['is_correct'] is True

    def test_attempt_marks_incorrect_when_wrong_choice_selected(self):
        student = UserFactory()
        question = QuestionFactory()
        AnswerChoiceFactory(question=question, is_correct=True)
        wrong_choice = AnswerChoiceFactory(question=question, is_correct=False)
        client = auth_client(student)

        response = client.post('/api/attempts/', {
            'question': question.id,
            'selected_choice': wrong_choice.id,
            'time_taken_seconds': 5,
        })

        assert response.status_code == 201
        assert response.data['is_correct'] is False

    def test_choice_from_other_question_is_rejected(self):
        student = UserFactory()
        question = QuestionFactory()
        other_question = QuestionFactory()
        mismatched_choice = AnswerChoiceFactory(question=other_question, is_correct=True)
        client = auth_client(student)

        response = client.post('/api/attempts/', {
            'question': question.id,
            'selected_choice': mismatched_choice.id,
            'time_taken_seconds': 5,
        })

        assert response.status_code == 400

    def test_student_only_sees_own_attempts(self):
        student_a = UserFactory()
        student_b = UserFactory()
        question = QuestionFactory()
        choice = AnswerChoiceFactory(question=question, is_correct=True)

        client_a = auth_client(student_a)
        client_a.post('/api/attempts/', {
            'question': question.id, 'selected_choice': choice.id, 'time_taken_seconds': 5,
        })

        client_b = auth_client(student_b)
        response = client_b.get('/api/attempts/')
        assert response.status_code == 200
        assert len(response.data) == 0


class TestTopicAccuracyAnalytics:
    def test_accuracy_reflects_attempt_history(self):
        student = UserFactory()
        question = QuestionFactory()
        correct_choice = AnswerChoiceFactory(question=question, is_correct=True)
        wrong_choice = AnswerChoiceFactory(question=question, is_correct=False)
        client = auth_client(student)

        client.post('/api/attempts/', {
            'question': question.id, 'selected_choice': correct_choice.id, 'time_taken_seconds': 5,
        })
        client.post('/api/attempts/', {
            'question': question.id, 'selected_choice': wrong_choice.id, 'time_taken_seconds': 5,
        })

        response = client.get('/api/analytics/topic-accuracy/')
        assert response.status_code == 200
        assert response.data[0]['total_attempts'] == 2
        assert response.data[0]['accuracy_percent'] == 50.0
