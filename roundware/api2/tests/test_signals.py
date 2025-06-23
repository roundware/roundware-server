import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from django.db.models.signals import post_save
from roundware.api2.signals import create_auth_token

@pytest.mark.django_db
class TestAuthTokenSignals:
    def setup_method(self):
        """Set up the test environment by connecting the signal"""
        # Connect the signal before each test
        post_save.connect(create_auth_token, sender=get_user_model())

    def teardown_method(self):
        """Clean up by disconnecting the signal after each test"""
        # Disconnect the signal after each test
        post_save.disconnect(create_auth_token, sender=get_user_model())

    def test_create_auth_token_on_user_creation(self):
        """Test that an auth token is created when a new user is created"""
        # Create a new user
        user = baker.make(get_user_model())
        
        # Verify that a token was created for the user
        token = Token.objects.get(user=user)
        assert token is not None
        assert token.user == user

    def test_no_token_created_for_existing_user(self):
        """Test that no new token is created when updating an existing user"""
        # Create a user first
        user = baker.make(get_user_model())
        initial_token = Token.objects.get(user=user)
        
        # Update the user
        user.first_name = "Updated"
        user.save()
        
        # Verify that no new token was created
        tokens = Token.objects.filter(user=user)
        assert tokens.count() == 1
        assert tokens.first() == initial_token

    def test_token_creation_with_custom_user_fields(self):
        """Test token creation works with users having custom fields"""
        # Create a user with custom fields
        user = baker.make(get_user_model(),
            username='testuser',
            email='test@example.com',
            is_active=True,
            is_staff=False
        )
        
        # Verify token creation
        token = Token.objects.get(user=user)
        assert token is not None
        assert token.user == user
        assert token.user.username == 'testuser'
        assert token.user.email == 'test@example.com'

    def test_multiple_users_token_creation(self):
        """Test token creation for multiple users"""
        # Create multiple users
        users = baker.make(get_user_model(), _quantity=3)
        
        # Verify each user has exactly one token
        for user in users:
            token = Token.objects.get(user=user)
            assert token is not None
            assert token.user == user
        
        # Verify total token count
        assert Token.objects.count() == 3

    def test_token_uniqueness(self):
        """Test that tokens are unique per user"""
        user = baker.make(get_user_model())
        
        # Try to manually create another token for the same user
        with pytest.raises(IntegrityError):
            Token.objects.create(user=user)
