import pytest
from model_bakery import baker
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from roundware.api2.permissions import AuthenticatedReadAdminWrite

@pytest.mark.django_db
class TestAuthenticatedReadAdminWrite:
    def setup_method(self):
        self.permission = AuthenticatedReadAdminWrite()
        self.view = APIView()
        self.factory = APIRequestFactory()
        self.regular_user = baker.make(User, is_staff=False)
        self.admin_user = baker.make(User, is_staff=True)
        self.anonymous_user = None

    def test_safe_methods_authenticated_user(self):
        """Test that authenticated users can access safe methods (GET, HEAD, OPTIONS)"""
        request = self.factory.get('/')
        request.user = self.regular_user
        assert self.permission.has_permission(request, self.view) is True

        request = self.factory.head('/')
        request.user = self.regular_user
        assert self.permission.has_permission(request, self.view) is True

        request = self.factory.options('/')
        request.user = self.regular_user
        assert self.permission.has_permission(request, self.view) is True

    def test_unsafe_methods_authenticated_user(self):
        """Test that non-admin authenticated users cannot access unsafe methods"""
        request = self.factory.post('/')
        request.user = self.regular_user
        assert self.permission.has_permission(request, self.view) is False

        request = self.factory.put('/')
        request.user = self.regular_user
        assert self.permission.has_permission(request, self.view) is False

        request = self.factory.delete('/')
        request.user = self.regular_user
        assert self.permission.has_permission(request, self.view) is False

    def test_unsafe_methods_admin_user(self):
        """Test that admin users can access unsafe methods"""
        request = self.factory.post('/')
        request.user = self.admin_user
        assert self.permission.has_permission(request, self.view) is True

        request = self.factory.put('/')
        request.user = self.admin_user
        assert self.permission.has_permission(request, self.view) is True

        request = self.factory.delete('/')
        request.user = self.admin_user
        assert self.permission.has_permission(request, self.view) is True

    def test_anonymous_user(self):
        """Test that anonymous users cannot access any methods"""
        request = self.factory.get('/')
        request.user = self.anonymous_user
        assert self.permission.has_permission(request, self.view) is False

        request = self.factory.post('/')
        request.user = self.anonymous_user
        assert self.permission.has_permission(request, self.view) is False 