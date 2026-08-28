from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import MeView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('me/', MeView.as_view(), name='me'),
]
