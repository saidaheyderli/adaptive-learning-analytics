from django.urls import path

from .views import TopicAccuracyView

urlpatterns = [
    path('topic-accuracy/', TopicAccuracyView.as_view(), name='topic-accuracy'),
]
