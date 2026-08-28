from django.urls import path

from .views import RecommendationsView, TopicAccuracyView

urlpatterns = [
    path('topic-accuracy/', TopicAccuracyView.as_view(), name='topic-accuracy'),
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
]
