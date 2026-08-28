import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_register_creates_user_and_returns_token():
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'newstudent',
        'email': 'new@example.com',
        'password': 'strongpass123',
        'role': 'student',
    })
    assert response.status_code == 201
    assert 'token' in response.data
    assert response.data['user']['role'] == 'student'


def test_register_rejects_short_password():
    client = APIClient()
    response = client.post('/api/auth/register/', {
        'username': 'newstudent',
        'email': 'new@example.com',
        'password': 'short',
        'role': 'student',
    })
    assert response.status_code == 400


def test_login_returns_token_for_valid_credentials():
    client = APIClient()
    client.post('/api/auth/register/', {
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'strongpass123',
        'role': 'student',
    })
    response = client.post('/api/auth/login/', {
        'username': 'loginuser',
        'password': 'strongpass123',
    })
    assert response.status_code == 200
    assert 'token' in response.data


def test_me_requires_authentication():
    client = APIClient()
    response = client.get('/api/auth/me/')
    assert response.status_code == 401
