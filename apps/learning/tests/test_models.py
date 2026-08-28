import pytest

from apps.learning.tests.factories import AnswerChoiceFactory, QuestionFactory, TopicFactory

pytestmark = pytest.mark.django_db


def test_topic_str():
    topic = TopicFactory(name='Recursion')
    assert str(topic) == 'Recursion'


def test_question_belongs_to_topic():
    topic = TopicFactory()
    question = QuestionFactory(topic=topic)
    assert question.topic == topic
    assert question in topic.questions.all()


def test_answer_choice_linked_to_question():
    question = QuestionFactory()
    correct = AnswerChoiceFactory(question=question, is_correct=True)
    wrong = AnswerChoiceFactory(question=question, is_correct=False)
    assert set(question.choices.all()) == {correct, wrong}
