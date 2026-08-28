from rest_framework.routers import DefaultRouter

from .views import AttemptViewSet, QuestionViewSet, TopicViewSet

router = DefaultRouter()
router.register('topics', TopicViewSet, basename='topic')
router.register('questions', QuestionViewSet, basename='question')
router.register('attempts', AttemptViewSet, basename='attempt')

urlpatterns = router.urls
