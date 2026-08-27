from django.conf import settings
from django.db import models


class Topic(models.Model):
    """A subject area questions are tagged with, e.g. 'Recursion', 'Loops'."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    """A single question belonging to a topic, with a chosen difficulty."""

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    prompt = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['topic', 'difficulty']

    def __str__(self):
        return f'[{self.topic.name}] {self.prompt[:50]}'


class AnswerChoice(models.Model):
    """One selectable answer option for a Question (multiple-choice)."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        marker = '✓' if self.is_correct else '✗'
        return f'{marker} {self.text}'


class Attempt(models.Model):
    """
    A single record of a student answering a question.

    This is the core data source the analytics layer reads from: every
    attempt captures correctness and time taken, which is enough to
    compute per-topic accuracy and, later, weakness signals.
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts')
    selected_choice = models.ForeignKey(
        AnswerChoice,
        on_delete=models.SET_NULL,
        null=True,
        related_name='selected_in_attempts',
    )
    is_correct = models.BooleanField()
    time_taken_seconds = models.PositiveIntegerField(
        help_text='Time the student spent on this question, in seconds.'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['student', 'question']),
        ]

    def __str__(self):
        result = 'correct' if self.is_correct else 'incorrect'
        return f'{self.student} — {self.question_id} ({result})'
