from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Attempt, Question, Topic
from .permissions import IsInstructorOrReadOnly
from .serializers import (
    AttemptReadSerializer,
    AttemptSubmitSerializer,
    QuestionSerializer,
    TopicSerializer,
)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsInstructorOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('topic').prefetch_related('choices')
    serializer_class = QuestionSerializer
    permission_classes = [IsInstructorOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AttemptViewSet(viewsets.ModelViewSet):
    """
    Students submit attempts and can only ever see their own.
    Instructors can see everyone's (used by the analytics layer / admin).
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = Attempt.objects.select_related('question__topic')
        if user.is_instructor:
            return qs
        return qs.filter(student=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AttemptSubmitSerializer
        return AttemptReadSerializer
