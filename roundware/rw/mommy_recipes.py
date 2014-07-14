from __future__ import unicode_literals
#from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from model_mommy.recipe import Recipe

from roundware.rw.models import Session
from roundware.settings import DEFAULT_SESSION_ID

# User = get_user_model()


basic_user = Recipe(
    User,
    username='user',
    password='password',
    first_name='Test',
    last_name='User',
    email='user@example.com',
)

default_session = Recipe(
    Session,
    id=DEFAULT_SESSION_ID)
