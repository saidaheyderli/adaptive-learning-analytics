import pytest
from django.urls import reverse


def test_dashboard_page_renders(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b'Progress Ledger' in response.content


def test_dashboard_page_has_login_form(client):
    response = client.get(reverse('dashboard'))
    assert b'login-form' in response.content
