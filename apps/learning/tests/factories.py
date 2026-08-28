import factory
from django.contrib.auth import get_user_model

from apps.learning.models import AnswerChoice, Attempt, Question, Topic

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    role = User.Role.STUDENT

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'strongpass123')
        user = model_class(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class InstructorFactory(UserFactory):
    role = User.Role.INSTRUCTOR


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    name = factory.Sequence(lambda n: f'Topic {n}')
    slug = factory.Sequence(lambda n: f'topic-{n}')


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    topic = factory.SubFactory(TopicFactory)
    prompt = factory.Sequence(lambda n: f'Question prompt {n}?')
    difficulty = Question.Difficulty.MEDIUM


class AnswerChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnswerChoice

    question = factory.SubFactory(QuestionFactory)
    text = factory.Sequence(lambda n: f'Choice {n}')
    is_correct = False


class AttemptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attempt

    student = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QuestionFactory)
    is_correct = True
    time_taken_seconds = 10
