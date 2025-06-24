import pytest
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, exceptions, authentication, permissions, throttling, parsers, renderers, negotiation, versioning
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView, get_view_name, get_view_description, exception_handler
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.versioning import URLPathVersioning
from model_bakery import baker
from django.db.models import QuerySet
from django.contrib.auth.models import User
import time
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.request import Request
from django.db import models
from django.test.utils import override_settings
from django.test.testcases import TransactionTestCase
from django.urls import reverse

# Test fixtures
@pytest.fixture
def api_rf():
    return APIRequestFactory()

@pytest.fixture
def sample_view_class():
    class TestView(APIView):
        """Test view description."""
        name = "Custom View Name"
        
        def get(self, request):
            return Response({'message': 'success'})
            
        def post(self, request):
            return Response({'message': 'created'}, status=status.HTTP_201_CREATED)
            
    return TestView

@pytest.fixture
def sample_view(sample_view_class):
    return sample_view_class()

@pytest.fixture
def unnamed_view():
    class TestUnnamedView(APIView):
        """Test unnamed view."""
        def get(self, request):
            return Response({'message': 'success'})
            
    return TestUnnamedView()

@pytest.fixture
def custom_view_class():
    class CustomView(APIView):
        """Custom view with specific settings."""
        renderer_classes = [api_settings.DEFAULT_RENDERER_CLASSES[0]]  # Only first renderer
        authentication_classes = []  # No authentication
        permission_classes = []  # No permissions
        throttle_classes = []  # No throttling
        
        def get(self, request):
            return Response({'message': 'custom'})
            
    return CustomView

@pytest.fixture
def custom_view(custom_view_class):
    return custom_view_class()

class TestAuthenticator(BaseAuthentication):
    def authenticate(self, request):
        return None
    
    def authenticate_header(self, request):
        return 'Bearer realm="api"'

@pytest.fixture
def auth_view_class():
    class AuthenticatedView(APIView):
        authentication_classes = [TestAuthenticator]
        
        def get(self, request):
            return Response({'message': 'authenticated'})
    
    return AuthenticatedView

# Test view name generation
def test_get_view_name_with_custom_name(sample_view):
    """Test get_view_name when view has custom name attribute."""
    assert get_view_name(sample_view) == "Custom View Name"

def test_get_view_name_without_custom_name(unnamed_view):
    """Test get_view_name generates name from class name."""
    assert get_view_name(unnamed_view) == "Test Unnamed"

def test_get_view_name_with_suffix(unnamed_view):
    """Test get_view_name with suffix."""
    unnamed_view.suffix = "List"
    assert get_view_name(unnamed_view) == "Test Unnamed List"

# Test view description
def test_get_view_description_from_docstring(sample_view):
    """Test get_view_description returns docstring."""
    assert get_view_description(sample_view) == "Test view description."

def test_get_view_description_html_format(sample_view):
    """Test get_view_description with HTML formatting."""
    desc = get_view_description(sample_view, html=True)
    assert "<p>Test view description.</p>" in desc

def test_get_view_description_custom_description(sample_view):
    """Test get_view_description with custom description attribute."""
    sample_view.description = "Custom description"
    assert get_view_description(sample_view) == "Custom description"

# Test exception handling
def test_exception_handler_handles_http404():
    """Test exception_handler converts Http404 to NotFound."""
    exc = Http404("Not found")
    response = exception_handler(exc, {})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {'detail': 'Not found'}

def test_exception_handler_handles_permission_denied():
    """Test exception_handler converts PermissionDenied to DRF PermissionDenied."""
    exc = PermissionDenied("No permission")
    response = exception_handler(exc, {})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data == {'detail': 'No permission'}

def test_exception_handler_handles_api_exception():
    """Test exception_handler handles APIException."""
    exc = exceptions.ValidationError({'field': 'Invalid'})
    response = exception_handler(exc, {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'field': 'Invalid'}

def test_exception_handler_with_auth_header():
    """Test exception_handler includes auth header when present."""
    exc = exceptions.AuthenticationFailed('Auth failed')
    exc.auth_header = 'Bearer realm="api"'
    response = exception_handler(exc, {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers.get('www-authenticate') == 'Bearer realm="api"'

# Test view methods
def test_api_view_options_method(api_rf, sample_view):
    """Test OPTIONS method returns metadata."""
    request = api_rf.options('/')
    response = sample_view.dispatch(request)
    assert response.status_code == status.HTTP_200_OK
    # Check for standard metadata fields
    assert 'name' in response.data
    assert 'description' in response.data
    assert 'renders' in response.data
    assert 'parses' in response.data
    assert response.data['name'] == 'Custom View Name'
    assert response.data['description'] == 'Test view description.'

def test_api_view_handles_method_not_allowed(api_rf, sample_view):
    """Test view handles unsupported HTTP method."""
    request = api_rf.put('/')  # Using PUT instead of POST since POST is implemented
    response = sample_view.dispatch(request)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_api_view_get_method(api_rf, sample_view):
    """Test GET method returns success response."""
    request = api_rf.get('/')
    response = sample_view.dispatch(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'message': 'success'}

# New tests for APIView class features

def test_api_view_default_settings(sample_view):
    """Test APIView default settings are properly set."""
    assert sample_view.renderer_classes == api_settings.DEFAULT_RENDERER_CLASSES
    assert sample_view.parser_classes == api_settings.DEFAULT_PARSER_CLASSES
    assert sample_view.authentication_classes == api_settings.DEFAULT_AUTHENTICATION_CLASSES
    assert sample_view.permission_classes == api_settings.DEFAULT_PERMISSION_CLASSES
    assert sample_view.content_negotiation_class == api_settings.DEFAULT_CONTENT_NEGOTIATION_CLASS
    assert sample_view.metadata_class == api_settings.DEFAULT_METADATA_CLASS

def test_api_view_custom_settings(custom_view):
    """Test APIView with custom settings."""
    assert len(custom_view.renderer_classes) == 1
    assert custom_view.authentication_classes == []
    assert custom_view.permission_classes == []
    assert custom_view.throttle_classes == []

def test_api_view_allowed_methods(sample_view):
    """Test allowed_methods property returns correct HTTP methods."""
    allowed = sample_view.allowed_methods
    assert 'GET' in allowed
    assert 'POST' in allowed
    assert 'PUT' not in allowed
    assert 'DELETE' not in allowed

def test_api_view_default_response_headers_single_renderer(custom_view):
    """Test default response headers with single renderer."""
    headers = custom_view.default_response_headers
    assert 'Allow' in headers
    assert 'Vary' not in headers
    assert 'GET' in headers['Allow']

def test_api_view_default_response_headers_multiple_renderers(sample_view):
    """Test default response headers with multiple renderers."""
    headers = sample_view.default_response_headers
    assert 'Allow' in headers
    assert 'Vary' in headers
    assert headers['Vary'] == 'Accept'

def test_api_view_csrf_exempt_decorator(sample_view_class):
    """Test that APIView is properly CSRF exempt."""
    view_func = sample_view_class.as_view()
    assert getattr(view_func, 'csrf_exempt', False) is True

def test_api_view_http_method_not_allowed(api_rf, sample_view):
    """Test method not allowed raises proper exception."""
    request = api_rf.put('/')  # Using PUT instead of DELETE
    response = sample_view.dispatch(request)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.data['detail'] == 'Method "PUT" not allowed.'

def test_api_view_options_allowed_methods(api_rf, sample_view):
    """Test OPTIONS request returns Allow header with correct methods."""
    request = api_rf.options('/')
    response = sample_view.dispatch(request)
    assert response.status_code == status.HTTP_200_OK
    assert 'allow' in response.headers
    allow_header = response.headers['allow'].split(', ')
    assert 'GET' in allow_header
    assert 'POST' in allow_header
    assert 'OPTIONS' in allow_header

def test_api_view_head_method(api_rf, sample_view_class):
    """Test HEAD method returns same headers as GET without content."""
    # Create a view class that explicitly handles HEAD
    class HeadTestView(sample_view_class):
        renderer_classes = [JSONRenderer]
        
        def get(self, request, *args, **kwargs):
            return Response({'message': 'success'})
            
        def head(self, request, *args, **kwargs):
            response = self.get(request, *args, **kwargs)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            response.content = b''
            return response
    
    view = HeadTestView()
    
    # Handle GET request
    get_request = api_rf.get('/', HTTP_ACCEPT='application/json')
    get_response = view.dispatch(get_request)
    get_response.accepted_renderer = JSONRenderer()
    get_response.accepted_media_type = "application/json"
    get_response.renderer_context = {}
    get_response.render()
    
    # Handle HEAD request
    head_request = api_rf.head('/', HTTP_ACCEPT='application/json')
    head_response = view.dispatch(head_request)
    
    assert head_response.status_code == get_response.status_code
    assert dict(head_response.headers) == dict(get_response.headers)
    assert head_response.content == b''

@pytest.mark.django_db
def test_api_view_queryset_evaluation_warning():
    """Test warning about direct queryset evaluation."""
    class TestQuerySet(QuerySet):
        def _fetch_all(self):
            raise RuntimeError(
                'Do not evaluate the `.queryset` attribute directly, '
                'as the result will be cached and reused between requests. '
                'Use `.all()` or call `.get_queryset()` instead.'
            )

    class ModelViewSet(APIView):
        queryset = TestQuerySet(model=User)

    with pytest.raises(RuntimeError) as exc_info:
        ModelViewSet.queryset._fetch_all()

    assert 'Do not evaluate the `.queryset` attribute directly' in str(exc_info.value)
    assert 'Use `.all()` or call `.get_queryset()` instead' in str(exc_info.value)

# New tests for permission handling
def test_permission_denied_not_authenticated(api_rf, auth_view_class):
    """Test permission_denied raises NotAuthenticated when no successful authenticator."""
    view = auth_view_class()
    request = api_rf.get('/')
    request.authenticators = [TestAuthenticator()]
    request.successful_authenticator = None
    
    with pytest.raises(exceptions.NotAuthenticated):
        view.permission_denied(request)

def test_permission_denied_with_message(api_rf, auth_view_class):
    """Test permission_denied raises PermissionDenied with custom message."""
    view = auth_view_class()
    request = api_rf.get('/')
    request.authenticators = []
    
    with pytest.raises(exceptions.PermissionDenied) as exc_info:
        view.permission_denied(request, message="Custom message")
    
    assert exc_info.value.detail == "Custom message"

# Test throttling
def test_throttled_exception(api_rf, sample_view):
    """Test throttled raises proper exception with wait time."""
    wait_time = 60
    
    with pytest.raises(exceptions.Throttled) as exc_info:
        sample_view.throttled(api_rf.get('/'), wait_time)
    
    assert exc_info.value.wait == wait_time

# Test authentication header
def test_get_authenticate_header(api_rf, auth_view_class):
    """Test get_authenticate_header returns proper header from authenticator."""
    view = auth_view_class()
    request = api_rf.get('/')
    
    auth_header = view.get_authenticate_header(request)
    assert auth_header == 'Bearer realm="api"'

def test_get_authenticate_header_no_authenticators(api_rf, sample_view):
    """Test get_authenticate_header returns None when no authenticators."""
    sample_view.authentication_classes = []
    assert sample_view.get_authenticate_header(api_rf.get('/')) is None

# Test parser context
def test_get_parser_context_default(api_rf, sample_view):
    """Test get_parser_context returns proper default context."""
    request = api_rf.get('/')
    context = sample_view.get_parser_context(request)
    
    assert context['view'] == sample_view
    assert context['args'] == ()
    assert context['kwargs'] == {}

def test_get_parser_context_with_args(api_rf, sample_view):
    """Test get_parser_context includes view args and kwargs."""
    request = api_rf.get('/')
    sample_view.args = ('arg1', 'arg2')
    sample_view.kwargs = {'key': 'value'}
    
    context = sample_view.get_parser_context(request)
    assert context['args'] == ('arg1', 'arg2')
    assert context['kwargs'] == {'key': 'value'}

# Test renderer context
def test_get_renderer_context_default(api_rf, sample_view):
    """Test get_renderer_context returns proper default context."""
    context = sample_view.get_renderer_context()
    
    assert context['view'] == sample_view
    assert context['args'] == ()
    assert context['kwargs'] == {}
    assert context['request'] is None

def test_get_renderer_context_with_request(api_rf, sample_view):
    """Test get_renderer_context includes request when available."""
    request = api_rf.get('/')
    sample_view.request = request
    sample_view.args = ('arg1',)
    sample_view.kwargs = {'key': 'value'}
    
    context = sample_view.get_renderer_context()
    assert context['request'] == request
    assert context['args'] == ('arg1',)
    assert context['kwargs'] == {'key': 'value'}

# Test combined scenarios
def test_authentication_and_permission_flow(api_rf):
    """Test complete authentication and permission flow."""
    class CustomAuthenticator(BaseAuthentication):
        def authenticate(self, request):
            if 'Token' in request.headers.get('Authorization', ''):
                return (None, None)
            return None
        
        def authenticate_header(self, request):
            return 'Token'

    class ProtectedView(APIView):
        authentication_classes = [CustomAuthenticator]
        
        def perform_authentication(self, request):
            super().perform_authentication(request)
            if not request.successful_authenticator:
                self.permission_denied(request)

        def get(self, request):
            return Response({'message': 'success'})

    view = ProtectedView()
    
    # Test unauthenticated request
    request = api_rf.get('/')
    request.authenticators = [CustomAuthenticator()]
    request.successful_authenticator = None
    
    with pytest.raises(exceptions.NotAuthenticated):
        view.permission_denied(request)
    
    # Test authenticated request
    request = api_rf.get('/', HTTP_AUTHORIZATION='Token xxx')
    response = view.dispatch(request)
    assert response.status_code == status.HTTP_200_OK

# Test custom classes for policy testing
class CustomRenderer(renderers.BaseRenderer):
    media_type = 'application/custom'
    format = 'custom'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class CustomParser(parsers.BaseParser):
    media_type = 'application/custom'
    
    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()

class CustomThrottle(throttling.BaseThrottle):
    def allow_request(self, request, view):
        return True

class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

class CustomNegotiation(negotiation.BaseContentNegotiation):
    def select_parser(self, request, parsers):
        return parsers[0]
    
    def select_renderer(self, request, renderers, format_suffix=None):
        return (renderers[0], renderers[0].media_type)

@pytest.fixture
def policy_view_class():
    class PolicyTestView(APIView):
        renderer_classes = [CustomRenderer]
        parser_classes = [CustomParser]
        authentication_classes = [TestAuthenticator]
        permission_classes = [CustomPermission]
        throttle_classes = [CustomThrottle]
        content_negotiation_class = CustomNegotiation
        format_suffix_patterns = True
        
        def get(self, request, *args, **kwargs):
            return Response({'message': 'success'})
    
    return PolicyTestView

# Test exception handler context
def test_get_exception_handler_context(api_rf, sample_view):
    """Test exception handler context contains all required keys."""
    request = api_rf.get('/')
    sample_view.request = request
    sample_view.args = ('test_arg',)
    sample_view.kwargs = {'test_key': 'test_value'}
    
    context = sample_view.get_exception_handler_context()
    
    assert context['view'] == sample_view
    assert context['args'] == ('test_arg',)
    assert context['kwargs'] == {'test_key': 'test_value'}
    assert context['request'] == request

# Test view information methods
def test_get_view_name_with_custom_function(sample_view):
    """Test get_view_name uses custom function from settings."""
    def custom_name_func(view):
        return "Custom Name"
    
    sample_view.settings.VIEW_NAME_FUNCTION = custom_name_func
    assert sample_view.get_view_name() == "Custom Name"

def test_get_view_description_with_html(sample_view):
    """Test get_view_description with HTML format."""
    def custom_desc_func(view, html):
        return "Custom Description" if not html else "<p>Custom Description</p>"
    
    sample_view.settings.VIEW_DESCRIPTION_FUNCTION = custom_desc_func
    assert sample_view.get_view_description(html=True) == "<p>Custom Description</p>"
    assert sample_view.get_view_description(html=False) == "Custom Description"

# Test format suffix
def test_get_format_suffix(policy_view_class):
    """Test format suffix retrieval."""
    view = policy_view_class()
    view.settings.FORMAT_SUFFIX_KWARG = 'format'
    
    result = view.get_format_suffix(format='json')
    assert result == 'json'
    
    result = view.get_format_suffix(wrong_kwarg='json')
    assert result is None

# Test policy instantiation methods
def test_get_renderers(policy_view_class):
    """Test renderer instantiation."""
    view = policy_view_class()
    renderers = view.get_renderers()
    
    assert len(renderers) == 1
    assert isinstance(renderers[0], CustomRenderer)

def test_get_parsers(policy_view_class):
    """Test parser instantiation."""
    view = policy_view_class()
    parsers = view.get_parsers()
    
    assert len(parsers) == 1
    assert isinstance(parsers[0], CustomParser)

def test_get_authenticators(policy_view_class):
    """Test authenticator instantiation."""
    view = policy_view_class()
    authenticators = view.get_authenticators()
    
    assert len(authenticators) == 1
    assert isinstance(authenticators[0], TestAuthenticator)

def test_get_permissions(policy_view_class):
    """Test permission instantiation."""
    view = policy_view_class()
    permissions = view.get_permissions()
    
    assert len(permissions) == 1
    assert isinstance(permissions[0], CustomPermission)

def test_get_throttles(policy_view_class):
    """Test throttle instantiation."""
    view = policy_view_class()
    throttles = view.get_throttles()
    
    assert len(throttles) == 1
    assert isinstance(throttles[0], CustomThrottle)

def test_get_content_negotiator_caching():
    """Test content negotiator caching behavior."""
    class TestView(APIView):
        content_negotiation_class = CustomNegotiation

    view = TestView()
    
    # First call should create and cache negotiator
    negotiator1 = view.get_content_negotiator()
    assert isinstance(negotiator1, CustomNegotiation)
    assert hasattr(view, '_negotiator')  # Should be cached after first call
    
    # Second call should return cached instance
    negotiator2 = view.get_content_negotiator()
    assert negotiator1 is negotiator2  # Should be the exact same instance

def test_get_exception_handler(sample_view):
    """Test exception handler retrieval."""
    def custom_exception_handler(exc, context):
        return Response({'error': str(exc)})
    
    sample_view.settings.EXCEPTION_HANDLER = custom_exception_handler
    handler = sample_view.get_exception_handler()
    
    assert handler == custom_exception_handler

# Test combined policy usage
def test_combined_policy_usage(api_rf, policy_view_class):
    """Test all policies working together in a request-response cycle."""
    view = policy_view_class()
    request = api_rf.get('/', HTTP_ACCEPT='application/custom')
    
    # Process request through various policies
    authenticators = view.get_authenticators()
    assert len(authenticators) == 1
    
    permissions = view.get_permissions()
    assert len(permissions) == 1
    assert permissions[0].has_permission(request, view)
    
    throttles = view.get_throttles()
    assert len(throttles) == 1
    assert throttles[0].allow_request(request, view)
    
    negotiator = view.get_content_negotiator()
    renderers = view.get_renderers()
    renderer, media_type = negotiator.select_renderer(request, renderers, None)
    assert isinstance(renderer, CustomRenderer)

# Test Content Negotiation
def test_perform_content_negotiation_success(api_rf, policy_view_class):
    """Test successful content negotiation."""
    view = policy_view_class()
    request = api_rf.get('/', HTTP_ACCEPT='application/custom')
    view.format_kwarg = None  # Initialize format_kwarg
    
    renderer, media_type = view.perform_content_negotiation(request)
    assert isinstance(renderer, CustomRenderer)
    assert media_type == 'application/custom'

def test_perform_content_negotiation_force(api_rf, policy_view_class):
    """Test forced content negotiation with invalid accept header."""
    view = policy_view_class()
    request = api_rf.get('/', HTTP_ACCEPT='invalid/type')
    
    renderer, media_type = view.perform_content_negotiation(request, force=True)
    assert isinstance(renderer, CustomRenderer)
    assert media_type == 'application/custom'

# Test Authentication
class AuthenticationWithUser(BaseAuthentication):
    def authenticate(self, request):
        if hasattr(request._request, 'user') and request._request.user.is_authenticated:
            return (request._request.user, None)
        return None

    def authenticate_header(self, request):
        return 'Bearer realm="api"'

@pytest.mark.django_db
def test_dispatch_full_cycle(api_rf):
    """Test complete dispatch cycle with all middleware and processing."""
    # Create a test user with model_bakery
    user = baker.make('auth.User', username='testuser')
    
    class TestView(APIView):
        authentication_classes = [AuthenticationWithUser]
        permission_classes = [permissions.IsAuthenticated]
        throttle_classes = []  # Disable throttling for this test
        
        def get(self, request, *args, **kwargs):
            return Response({
                'user': request.user.username,
                'version': request.version,
                'accepted_media_type': request.accepted_media_type
            })

    view = TestView()
    request = api_rf.get('/', HTTP_ACCEPT='application/json')
    
    # Initialize middleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    auth_middleware = AuthenticationMiddleware(lambda x: None)
    auth_middleware.process_request(request)
    
    # Set up the user
    request.user = user
    
    # Set up the view
    view.format_kwarg = None
    view.headers = {}
    
    # Dispatch the request
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user'] == 'testuser'
    assert response.data['accepted_media_type'] == 'application/json'

@pytest.mark.django_db
def test_perform_authentication_success(api_rf):
    """Test successful authentication."""
    user = baker.make('auth.User', username='testuser')
    
    class AuthView(APIView):
        authentication_classes = [AuthenticationWithUser]

    view = AuthView()
    request = api_rf.get('/')
    request.user = user
    request = view.initialize_request(request)
    view.perform_authentication(request)

    assert hasattr(request, 'user')
    assert request.user.is_authenticated
    assert request.user.username == 'testuser'

class DenyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False

@pytest.mark.django_db
def test_check_permissions_fail(api_rf):
    """Test failed permission check."""
    user = baker.make('auth.User', username='testuser')
    
    class RestrictedView(APIView):
        authentication_classes = [AuthenticationWithUser]  # Add authentication
        permission_classes = [DenyPermission]

    view = RestrictedView()
    request = api_rf.get('/')
    request.user = user
    request = view.initialize_request(request)
    view.perform_authentication(request)  # Authenticate first

    with pytest.raises(exceptions.PermissionDenied) as exc_info:
        view.check_permissions(request)
    assert exc_info.value.detail == "You do not have permission to perform this action."

@pytest.mark.django_db
def test_check_object_permissions(api_rf):
    """Test object permission check."""
    user = baker.make('auth.User', username='testuser')
    
    class ObjectDenyPermission(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return False

    class RestrictedObjectView(APIView):
        authentication_classes = [AuthenticationWithUser]
        permission_classes = [ObjectDenyPermission]

    view = RestrictedObjectView()
    request = api_rf.get('/')
    request.user = user
    request = view.initialize_request(request)
    view.perform_authentication(request)
    test_obj = object()

    with pytest.raises(exceptions.PermissionDenied):
        view.check_object_permissions(request, test_obj)

@pytest.mark.django_db
def test_combined_policy_implementation(api_rf):
    """Test all policy implementations working together."""
    user = baker.make('auth.User', username='testuser')
    
    class CombinedView(APIView):
        authentication_classes = [AuthenticationWithUser]
        permission_classes = [permissions.IsAuthenticated]
        throttle_classes = [CustomThrottle]
        renderer_classes = [CustomRenderer]
        versioning_class = CustomURLVersioning

        def get(self, request, *args, **kwargs):
            return Response({'version': request.version})

    view = CombinedView()
    request = api_rf.get('/v2.0/endpoint/', HTTP_ACCEPT='application/custom')
    
    # Set up the user
    request.user = user
    
    # Set up kwargs for the view
    view.kwargs = {'version': '2.0'}
    
    # Initialize request with proper context
    request = view.initialize_request(request)
    
    # Initialize format_kwarg
    view.format_kwarg = None
    view.headers = {}
    
    # Test authentication
    view.perform_authentication(request)
    assert request.user.is_authenticated
    assert request.user.username == 'testuser'
    
    # Test permissions
    view.check_permissions(request)
    
    # Test throttling
    view.check_throttles(request)
    
    # Test content negotiation
    renderer, media_type = view.perform_content_negotiation(request)
    assert isinstance(renderer, CustomRenderer)
    assert media_type == 'application/custom'
    
    # Test complete request handling using the view's dispatch
    request = api_rf.get('/v2.0/endpoint/', HTTP_ACCEPT='application/custom')
    request.user = user
    response = view.dispatch(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['version'] == '1.0'  # Default version is expected to be '1.0'

# Test dispatch methods
@pytest.mark.django_db
def test_initialize_request(api_rf):
    """Test initialize_request properly sets up the request object."""
    class TestView(APIView):
        def get(self, request):
            return Response({'message': 'success'})

    view = TestView()
    django_request = api_rf.get('/', HTTP_ACCEPT='application/json')
    
    request = view.initialize_request(django_request)
    
    assert isinstance(request, Request)
    assert len(request.parsers) == len(view.get_parsers())
    assert len(request.authenticators) == len(view.get_authenticators())
    assert request.negotiator.__class__ == view.get_content_negotiator().__class__
    assert request.parser_context['view'] == view

@pytest.mark.django_db
def test_finalize_response_with_response_object(api_rf):
    """Test finalize_response with DRF Response object."""
    class TestView(APIView):
        def get(self, request):
            return Response({'message': 'success'})

    view = TestView()
    request = view.initialize_request(api_rf.get('/', HTTP_ACCEPT='application/json'))
    view.format_kwarg = None
    
    # Initialize view headers
    view.headers = {}
    
    # Perform content negotiation first
    neg = view.perform_content_negotiation(request)
    request.accepted_renderer, request.accepted_media_type = neg
    
    response = view.finalize_response(request, Response({'message': 'test'}))
    
    assert isinstance(response, Response)
    assert response.accepted_renderer == request.accepted_renderer
    assert response.accepted_media_type == request.accepted_media_type
    assert 'message' in response.data

@pytest.mark.django_db
def test_finalize_response_with_vary_headers(api_rf):
    """Test finalize_response properly handles Vary headers."""
    class TestView(APIView):
        def get(self, request):
            return Response({'message': 'success'})

    view = TestView()
    request = view.initialize_request(api_rf.get('/', HTTP_ACCEPT='application/json'))
    view.format_kwarg = None
    
    # Initialize view headers
    view.headers = {'Vary': 'Accept-Version', 'Custom-Header': 'Value'}
    
    # Perform content negotiation first
    neg = view.perform_content_negotiation(request)
    request.accepted_renderer, request.accepted_media_type = neg
    
    response = view.finalize_response(request, Response({'message': 'test'}))
    
    assert 'vary' in response.headers
    assert 'Accept-Version' in response.headers['vary']
    assert response.headers['custom-header'] == 'Value'

# Test Versioning
class CustomURLVersioning(versioning.BaseVersioning):
    default_version = '1.0'
    
    def determine_version(self, request, *args, **kwargs):
        # First try to get version from kwargs
        version = getattr(request, 'version', None)
        if not version:
            version = kwargs.get('version', None)
        if not version and hasattr(request, 'parser_context'):
            version = request.parser_context.get('kwargs', {}).get('version', None)
        if not version:
            version = self.default_version
        return version

def test_determine_version_none(api_rf, sample_view):
    """Test version determination when versioning is disabled."""
    request = api_rf.get('/')
    version, scheme = sample_view.determine_version(request)
    assert version is None
    assert scheme is None

def test_determine_version_custom(api_rf):
    """Test custom version determination."""
    class VersionedView(APIView):
        versioning_class = CustomURLVersioning

    view = VersionedView()
    request = api_rf.get('/v2.0/endpoint/')
    request.parser_context = {'kwargs': {'version': '2.0'}}

    version = view.determine_version(request)[0]  # Get just the version part
    assert version == '2.0'  # Check version

# Test dispatch method comprehensive scenarios
@pytest.mark.django_db
def test_dispatch_method_get_success(api_rf):
    """Test successful GET request dispatch."""
    class TestDispatchView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({'method': 'get', 'args': args, 'kwargs': kwargs})

    view = TestDispatchView()
    request = api_rf.get('/test/')
    response = view.dispatch(request, test_arg='value')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'method': 'get', 'args': (), 'kwargs': {'test_arg': 'value'}}

@pytest.mark.django_db
def test_dispatch_method_post_with_data(api_rf):
    """Test POST request dispatch with data."""
    class TestDispatchView(APIView):
        def post(self, request, *args, **kwargs):
            return Response({'received_data': request.data})

    view = TestDispatchView()
    post_data = {'key': 'value'}
    request = api_rf.post('/test/', post_data, format='json')
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['received_data'] == post_data

@pytest.mark.django_db
def test_dispatch_method_not_allowed(api_rf):
    """Test dispatch with unsupported HTTP method."""
    class TestDispatchView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({'method': 'get'})

    view = TestDispatchView()
    request = api_rf.delete('/test/')  # DELETE not implemented
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

@pytest.mark.django_db
def test_dispatch_with_exception_handling(api_rf):
    """Test dispatch handles exceptions properly."""
    class TestDispatchView(APIView):
        def get(self, request, *args, **kwargs):
            raise exceptions.ValidationError(['Test error'])

    view = TestDispatchView()
    request = api_rf.get('/test/')
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[0] == 'Test error'

@pytest.mark.django_db
def test_dispatch_with_custom_args_kwargs(api_rf):
    """Test dispatch passes args and kwargs correctly."""
    class TestDispatchView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({
                'args': args,
                'kwargs': kwargs
            })

    view = TestDispatchView()
    request = api_rf.get('/test/')
    response = view.dispatch(request, 'arg1', 'arg2', key1='value1', key2='value2')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['args'] == ('arg1', 'arg2')
    assert response.data['kwargs'] == {'key1': 'value1', 'key2': 'value2'}

# Test options method comprehensive scenarios
@pytest.mark.django_db
def test_options_method_with_metadata(api_rf):
    """Test OPTIONS request with metadata class."""
    class CustomMetadata:
        def determine_metadata(self, request, view):
            return {
                'name': view.get_view_name(),
                'description': view.get_view_description(),
                'custom_field': 'test_value'
            }

    class TestOptionsView(APIView):
        metadata_class = CustomMetadata
        name = 'Test View'
        description = 'Test Description'

    view = TestOptionsView()
    request = api_rf.options('/test/')
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Test View'
    assert response.data['description'] == 'Test Description'
    assert response.data['custom_field'] == 'test_value'

@pytest.mark.django_db
def test_options_method_without_metadata_class(api_rf):
    """Test OPTIONS request when metadata_class is None."""
    class TestOptionsView(APIView):
        metadata_class = None

    view = TestOptionsView()
    request = api_rf.options('/test/')
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

@pytest.mark.django_db
def test_dispatch_authentication_flow(api_rf):
    """Test dispatch with authentication flow."""
    user = baker.make('auth.User', username='testuser')
    
    class TestAuthView(APIView):
        authentication_classes = [AuthenticationWithUser]
        permission_classes = [permissions.IsAuthenticated]
        
        def get(self, request, *args, **kwargs):
            return Response({'username': request.user.username})

    view = TestAuthView()
    request = api_rf.get('/test/')
    request.user = user
    response = view.dispatch(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'testuser'

@pytest.mark.django_db
def test_dispatch_with_headers(api_rf):
    """Test dispatch adds default headers to response."""
    class TestHeaderView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({'data': 'test'})

    view = TestHeaderView()
    request = api_rf.get('/test/')
    response = view.dispatch(request)
    
    assert 'allow' in response.headers
    assert 'GET, OPTIONS' in response.headers['allow']

@pytest.mark.django_db
def test_dispatch_with_custom_headers(api_rf):
    """Test dispatch with custom headers."""
    class TestCustomHeaderView(APIView):
        def get(self, request, *args, **kwargs):
            return Response(
                {'data': 'test'},
                headers={'Custom-Header': 'test-value'}
            )

    view = TestCustomHeaderView()
    request = api_rf.get('/test/')
    response = view.dispatch(request)
    
    assert 'custom-header' in response.headers
    assert response.headers['custom-header'] == 'test-value'

# Test raise_uncaught_exception method
@pytest.mark.django_db
def test_raise_uncaught_exception_debug_mode(api_rf, settings):
    """Test uncaught exception handling in DEBUG mode with different renderer formats."""
    settings.DEBUG = True
    
    class TestRenderer:
        format = 'json'  # Test with non-html format first
    
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            raise ValueError("Test uncaught error")
    
    view = TestView()
    request = api_rf.get('/test/')
    request.force_plaintext_errors_called = None
    request.force_plaintext_errors = lambda x: setattr(request, 'force_plaintext_errors_called', x)
    request.accepted_renderer = TestRenderer()
    view.request = request
    
    with pytest.raises(ValueError) as exc_info:
        view.raise_uncaught_exception(ValueError("Test uncaught error"))
    assert str(exc_info.value) == "Test uncaught error"
    assert request.force_plaintext_errors_called is True  # Should use plaintext for non-html format

@pytest.mark.django_db
def test_raise_uncaught_exception_debug_mode_html_renderer(api_rf, settings):
    """Test uncaught exception handling in DEBUG mode with HTML renderer."""
    settings.DEBUG = True
    
    class TestRenderer:
        format = 'html'  # Test with html format
    
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            raise ValueError("Test uncaught error")
    
    view = TestView()
    request = api_rf.get('/test/')
    request.force_plaintext_errors_called = None
    request.force_plaintext_errors = lambda x: setattr(request, 'force_plaintext_errors_called', x)
    request.accepted_renderer = TestRenderer()
    view.request = request
    
    with pytest.raises(ValueError) as exc_info:
        view.raise_uncaught_exception(ValueError("Test uncaught error"))
    assert str(exc_info.value) == "Test uncaught error"
    assert request.force_plaintext_errors_called is False  # Should not use plaintext for html format

@pytest.mark.django_db
def test_raise_uncaught_exception_debug_mode_api_renderer(api_rf, settings):
    """Test uncaught exception handling in DEBUG mode with API renderer."""
    settings.DEBUG = True
    
    class TestRenderer:
        format = 'api'  # Test with api format
    
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            raise ValueError("Test uncaught error")
    
    view = TestView()
    request = api_rf.get('/test/')
    request.force_plaintext_errors_called = None
    request.force_plaintext_errors = lambda x: setattr(request, 'force_plaintext_errors_called', x)
    request.accepted_renderer = TestRenderer()
    view.request = request
    
    with pytest.raises(ValueError) as exc_info:
        view.raise_uncaught_exception(ValueError("Test uncaught error"))
    assert str(exc_info.value) == "Test uncaught error"
    assert request.force_plaintext_errors_called is False  # Should not use plaintext for api format

@pytest.mark.django_db
def test_raise_uncaught_exception_production_mode(api_rf, settings):
    """Test uncaught exception handling in production mode (DEBUG=False)."""
    settings.DEBUG = False
    
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            raise ValueError("Test uncaught error")
    
    view = TestView()
    request = api_rf.get('/test/')
    view.request = request
    
    with pytest.raises(ValueError) as exc_info:
        view.raise_uncaught_exception(ValueError("Test uncaught error"))
    assert str(exc_info.value) == "Test uncaught error"

@pytest.mark.django_db
def test_raise_uncaught_exception_no_renderer_format(api_rf, settings):
    """Test uncaught exception handling when renderer has no format attribute."""
    settings.DEBUG = True
    
    class TestRenderer:
        pass  # No format attribute
    
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            raise ValueError("Test uncaught error")
    
    view = TestView()
    request = api_rf.get('/test/')
    request.accepted_renderer = TestRenderer()
    view.request = request
    
    # When format is missing, AttributeError should be raised
    with pytest.raises(AttributeError) as exc_info:
        view.raise_uncaught_exception(ValueError("Test uncaught error"))
    
    assert str(exc_info.value) == "'TestRenderer' object has no attribute 'format'"

# Test handle_exception response handling
@pytest.mark.django_db
def test_handle_exception_with_none_response(api_rf):
    """Test handle_exception when exception_handler returns None."""
    class TestView(APIView):
        def get_exception_handler(self):
            # Override to return a handler that always returns None
            return lambda exc, context: None

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request

    # Should raise the original exception when handler returns None
    with pytest.raises(ValueError) as exc_info:
        view.handle_exception(ValueError("Test error"))
    assert str(exc_info.value) == "Test error"

@pytest.mark.django_db
def test_handle_exception_with_custom_response(api_rf):
    """Test handle_exception when exception_handler returns a response."""
    class TestView(APIView):
        def get_exception_handler(self):
            def custom_handler(exc, context):
                return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            return custom_handler

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request

    response = view.handle_exception(ValueError("Test error"))
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'error': 'Test error'}
    assert response.exception is True  # Verify exception flag is set

@pytest.mark.django_db
def test_handle_exception_sets_exception_flag(api_rf):
    """Test handle_exception sets exception flag on response."""
    class TestView(APIView):
        def get_exception_handler(self):
            def custom_handler(exc, context):
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return custom_handler

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request

    response = view.handle_exception(Exception("Test error"))
    
    assert response.exception is True
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.django_db
def test_handle_exception_preserves_response_data(api_rf):
    """Test handle_exception preserves custom response data."""
    class TestView(APIView):
        def get_exception_handler(self):
            def custom_handler(exc, context):
                return Response(
                    {'detail': 'Custom error', 'extra': 'data'},
                    status=status.HTTP_400_BAD_REQUEST,
                    headers={'Custom-Header': 'test'}
                )
            return custom_handler

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request

    response = view.handle_exception(ValueError("Test error"))
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'detail': 'Custom error', 'extra': 'data'}
    assert response.exception is True
    assert response.headers['custom-header'] == 'test'

# Test exception handler and context logic (lines 456-461)
@pytest.mark.django_db
def test_exception_handler_gets_proper_context(api_rf):
    """Test that exception handler receives the proper context."""
    context_received = {}
    
    class TestView(APIView):
        def get_exception_handler(self):
            def custom_handler(exc, context):
                # Store the received context for verification
                context_received.update(context)
                return Response({'error': str(exc)})
            return custom_handler
            
        def get_exception_handler_context(self):
            return {'custom_context': 'test_value', 'view': self}

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request
    
    view.handle_exception(ValueError("Test error"))
    
    # Verify the context was properly passed to the handler
    assert 'custom_context' in context_received
    assert context_received['custom_context'] == 'test_value'
    assert context_received['view'] == view

@pytest.mark.django_db
def test_exception_handler_chain(api_rf):
    """Test the complete exception handler chain from get_exception_handler to response."""
    handler_called = False
    
    class TestView(APIView):
        def get_exception_handler(self):
            def custom_handler(exc, context):
                nonlocal handler_called
                handler_called = True
                return Response({'error': str(exc)})
            return custom_handler

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request
    
    response = view.handle_exception(ValueError("Test error"))
    
    assert handler_called  # Verify handler was actually called
    assert isinstance(response, Response)
    assert response.data == {'error': 'Test error'}

@pytest.mark.django_db
def test_exception_handler_none_raises_original_exception(api_rf):
    """Test that None response from handler raises the original exception."""
    class TestView(APIView):
        def get_exception_handler(self):
            return lambda exc, context: None

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request
    
    original_exc = ValueError("Original error")
    
    # The handler returns None, so raise_uncaught_exception should be called
    with pytest.raises(ValueError) as exc_info:
        view.handle_exception(original_exc)
    
    # Verify it's the same exception
    assert str(exc_info.value) == "Original error"

@pytest.mark.django_db
def test_custom_exception_handler_response_types(api_rf):
    """Test different response types from exception handler."""
    class TestView(APIView):
        def get_exception_handler(self):
            def custom_handler(exc, context):
                if isinstance(exc, ValueError):
                    return Response({'error': 'value_error'})
                elif isinstance(exc, TypeError):
                    return Response({'error': 'type_error'})
                return None  # For other exceptions
            return custom_handler

    view = TestView()
    request = api_rf.get('/test/')
    view.request = request
    
    # Test ValueError handling
    response = view.handle_exception(ValueError())
    assert response.data == {'error': 'value_error'}
    
    # Test TypeError handling
    response = view.handle_exception(TypeError())
    assert response.data == {'error': 'type_error'}
    
    # Test unhandled exception type
    with pytest.raises(KeyError):
        view.handle_exception(KeyError())

# Test queryset evaluation (lines 68, 91, 101)
@pytest.mark.django_db
def test_queryset_evaluation_in_as_view():
    """Test queryset evaluation prevention in as_view."""
    class TestViewSet(APIView):
        queryset = User.objects.all()

    view_func = TestViewSet.as_view()
    assert hasattr(view_func.cls.queryset, '_fetch_all')
    
    # Test direct evaluation prevention
    with pytest.raises(RuntimeError) as exc_info:
        list(view_func.cls.queryset)
    assert "Do not evaluate the `.queryset` attribute directly" in str(exc_info.value)

# Test authenticate_header branch (line 253->exit)
def test_get_authenticate_header_chain(api_rf):
    """Test authenticate_header chain with multiple authenticators."""
    class NoHeaderAuth(BaseAuthentication):
        def authenticate(self, request):
            return None
        
        def authenticate_header(self, request):
            return None
    
    class HeaderAuth(BaseAuthentication):
        def authenticate(self, request):
            return None
        
        def authenticate_header(self, request):
            return 'Basic realm="api"'
    
    # Test with HeaderAuth first - should return its header
    class ChainedAuthView1(APIView):
        authentication_classes = [HeaderAuth, NoHeaderAuth]
    
    view1 = ChainedAuthView1()
    request = api_rf.get('/')
    assert view1.get_authenticate_header(request) == 'Basic realm="api"'
    
    # Test with NoHeaderAuth first - should return None
    class ChainedAuthView2(APIView):
        authentication_classes = [NoHeaderAuth, HeaderAuth]
    
    view2 = ChainedAuthView2()
    assert view2.get_authenticate_header(request) is None

# Test content negotiator branch (line 314)
def test_content_negotiator_caching():
    """Test content negotiator caching behavior."""
    class TestView(APIView):
        content_negotiation_class = CustomNegotiation

    view = TestView()
    
    # First call should create and cache negotiator
    negotiator1 = view.get_content_negotiator()
    assert isinstance(negotiator1, CustomNegotiation)
    assert hasattr(view, '_negotiator')  # Should be cached after first call
    
    # Second call should return cached instance
    negotiator2 = view.get_content_negotiator()
    assert negotiator1 is negotiator2  # Should be the exact same instance

# Test content negotiation branches (lines 344->exit, 345->344)
def test_perform_content_negotiation_error_handling(api_rf):
    """Test content negotiation error handling."""
    class FailingNegotiator(negotiation.BaseContentNegotiation):
        def select_renderer(self, request, renderers, format_suffix=None):
            raise Exception("Negotiation failed")

    class TestView(APIView):
        content_negotiation_class = FailingNegotiator
        renderer_classes = [JSONRenderer]

    view = TestView()
    request = api_rf.get('/')
    view.format_kwarg = None
    
    # Should raise when force=False
    with pytest.raises(Exception) as exc_info:
        view.perform_content_negotiation(request)
    assert str(exc_info.value) == "Negotiation failed"
    
    # Should use first renderer when force=True
    renderer, media_type = view.perform_content_negotiation(request, force=True)
    assert isinstance(renderer, JSONRenderer)

# Test throttle durations (lines 360, 365-371)
def test_check_throttles_with_multiple_durations(api_rf):
    """Test throttling with multiple duration values."""
    class Throttle1(throttling.BaseThrottle):
        def allow_request(self, request, view):
            return False
        
        def wait(self):
            return 60  # 60 seconds

    class Throttle2(throttling.BaseThrottle):
        def allow_request(self, request, view):
            return False
        
        def wait(self):
            return 120  # 120 seconds

    class ThrottledView(APIView):
        throttle_classes = [Throttle1, Throttle2]

    view = ThrottledView()
    request = api_rf.get('/')
    
    with pytest.raises(exceptions.Throttled) as exc_info:
        view.check_throttles(request)
    
    # Should use maximum duration
    assert exc_info.value.wait == 120

# Test initialize request branches (lines 429->439, 431-432)
def test_initialize_request_parser_context(api_rf):
    """Test initialize_request with custom parser context."""
    class TestView(APIView):
        def get_parser_context(self, request):
            context = super().get_parser_context(request)
            context.update({
                'test_key': 'test_value',
                'view_name': self.__class__.__name__
            })
            return context

    view = TestView()
    request = api_rf.get('/')
    
    initialized_request = view.initialize_request(request)
    assert initialized_request.parser_context['test_key'] == 'test_value'
    assert initialized_request.parser_context['view_name'] == 'TestView'

# Test handle exception branches (lines 456-461)
def test_handle_exception_complete_flow(api_rf):
    """Test complete exception handling flow."""
    handled_exc = None
    handled_context = None
    
    def custom_handler(exc, context):
        nonlocal handled_exc, handled_context
        handled_exc = exc
        handled_context = context
        if isinstance(exc, ValueError):
            return Response({'error': str(exc)}, status=400)
        return None

    class TestView(APIView):
        def get_exception_handler(self):
            return custom_handler
        
        def get_exception_handler_context(self):
            context = super().get_exception_handler_context()
            context['extra'] = 'test'
            return context

    view = TestView()
    request = api_rf.get('/')
    view.request = request
    
    # Test handled exception
    response = view.handle_exception(ValueError("Test error"))
    assert response.status_code == 400
    assert response.data == {'error': 'Test error'}
    assert handled_context['extra'] == 'test'
    
    # Test unhandled exception
    with pytest.raises(TypeError) as exc_info:
        view.handle_exception(TypeError("Unhandled error"))
    assert isinstance(handled_exc, TypeError)

# Test dispatch branch (line 504)
def test_dispatch_invalid_method_handling(api_rf):
    """Test dispatch handling of invalid HTTP methods."""
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({'method': 'get'})
        
        def http_method_not_allowed(self, request, *args, **kwargs):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    view = TestView()
    request = api_rf.generic('INVALID', '/')  # Use generic() to create request with custom method
    
    response = view.dispatch(request)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

@pytest.mark.django_db
def test_queryset_evaluation_warning_with_fetch():
    """Test queryset evaluation warning when _fetch_all is called directly."""
    class TestQuerySet(QuerySet):
        def _fetch_all(self):
            raise RuntimeError(
                'Do not evaluate the `.queryset` attribute directly, '
                'as the result will be cached and reused between requests. '
                'Use `.all()` or call `.get_queryset()` instead.'
            )

    class TestModel(models.Model):
        class Meta:
            app_label = 'auth'

    class ModelViewSet(APIView):
        queryset = TestQuerySet(model=TestModel)

    view = ModelViewSet.as_view()
    with pytest.raises(RuntimeError) as exc_info:
        view.cls.queryset._fetch_all()
    assert 'Do not evaluate the `.queryset` attribute directly' in str(exc_info.value)

def test_authenticate_header_chain_exit(api_rf):
    """Test authenticate_header chain exit condition (line 253->exit)."""
    class NoHeaderAuth(BaseAuthentication):
        def authenticate(self, request):
            return None
        
        def authenticate_header(self, request):
            return None

    class HeaderAuth(BaseAuthentication):
        def authenticate(self, request):
            return None
        
        def authenticate_header(self, request):
            return None

    class TestView(APIView):
        authentication_classes = [NoHeaderAuth, HeaderAuth]

    view = TestView()
    request = api_rf.get('/')
    # Both authenticators return None, so get_authenticate_header should return None
    assert view.get_authenticate_header(request) is None

def test_content_negotiation_empty_renderers(api_rf):
    """Test content negotiation with empty renderers (lines 344->exit, 345->344)."""
    class TestView(APIView):
        renderer_classes = []

    view = TestView()
    request = api_rf.get('/')
    
    # Should raise exception when no renderers available
    with pytest.raises(Exception) as exc_info:
        view.perform_content_negotiation(request)
    
    # Try with force=True, should still raise as no renderers available
    with pytest.raises(Exception) as exc_info:
        view.perform_content_negotiation(request, force=True)

def test_initialize_request_complex_context(api_rf):
    """Test initialize request with complex context (lines 429->439, 431-432)."""
    class CustomParser(parsers.BaseParser):
        media_type = 'application/custom'
        def parse(self, stream, media_type=None, parser_context=None):
            return stream.read()

    class CustomAuth(BaseAuthentication):
        def authenticate(self, request):
            return None

    class CustomNegotiator(negotiation.BaseContentNegotiation):
        def select_parser(self, request, parsers):
            return parsers[0]
        
        def select_renderer(self, request, renderers, format_suffix=None):
            return (renderers[0], renderers[0].media_type)

    class TestView(APIView):
        parser_classes = [CustomParser]
        authentication_classes = [CustomAuth]
        content_negotiation_class = CustomNegotiator
        
        def get_parser_context(self, request):
            context = super().get_parser_context(request)
            context.update({
                'custom_key': 'custom_value',
                'nested': {
                    'key': 'value'
                }
            })
            return context

    view = TestView()
    request = api_rf.get('/')
    
    initialized_request = view.initialize_request(request)
    assert isinstance(initialized_request.parser_context, dict)
    assert initialized_request.parser_context['custom_key'] == 'custom_value'
    assert initialized_request.parser_context['nested']['key'] == 'value'
    assert len(initialized_request.parsers) == 1
    assert isinstance(initialized_request.parsers[0], CustomParser)
    assert len(initialized_request.authenticators) == 1
    assert isinstance(initialized_request.authenticators[0], CustomAuth)
    assert isinstance(initialized_request.negotiator, CustomNegotiator)

def test_exception_handler_complete_flow():
    """Test complete exception handler flow (lines 456-461)."""
    class CustomException(exceptions.APIException):
        status_code = 400
        default_detail = 'Custom error'
        auth_header = 'Bearer realm="api"'
        wait = 30

    # Test with string detail
    exc1 = CustomException()
    response1 = exception_handler(exc1, {})
    assert response1.status_code == 400
    assert response1.data == {'detail': 'Custom error'}
    assert response1['WWW-Authenticate'] == 'Bearer realm="api"'
    assert response1['Retry-After'] == '30'

    # Test with list detail
    exc2 = CustomException()
    exc2.detail = ['Error 1', 'Error 2']
    response2 = exception_handler(exc2, {})
    assert response2.status_code == 400
    assert response2.data == ['Error 1', 'Error 2']

    # Test with dict detail
    exc3 = CustomException()
    exc3.detail = {'field1': 'Error 1', 'field2': 'Error 2'}
    response3 = exception_handler(exc3, {})
    assert response3.status_code == 400
    assert response3.data == {'field1': 'Error 1', 'field2': 'Error 2'}

# Test set_rollback function
@pytest.mark.django_db(transaction=True)
def test_set_rollback_with_atomic_requests(settings):
    """Test set_rollback when ATOMIC_REQUESTS is True and in atomic block."""
    from django.db import connections, transaction
    from rest_framework.views import set_rollback
    
    # Configure the test database to use atomic requests
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
    
    # Start a transaction to simulate being in an atomic block
    with transaction.atomic():
        # Call set_rollback
        result = set_rollback()
        
        # Verify rollback was set and function returns None
        assert connections['default'].needs_rollback
        assert result is None

@pytest.mark.django_db(transaction=True)
def test_set_rollback_without_atomic_requests(settings):
    """Test set_rollback when ATOMIC_REQUESTS is False."""
    from django.db import connections
    from rest_framework.views import set_rollback
    
    # Configure the test database to not use atomic requests
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = False
    
    # Call set_rollback
    result = set_rollback()
    
    # Verify rollback was not set and function returns None
    assert not connections['default'].needs_rollback
    assert result is None

@pytest.mark.django_db(transaction=True)
def test_set_rollback_outside_atomic_block(settings):
    """Test set_rollback when not in atomic block."""
    from django.db import connections, transaction
    from rest_framework.views import set_rollback
    from django.test.testcases import TransactionTestCase
    
    # Configure the test database to use atomic requests
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
    
    # Get the connection
    connection = connections['default']
    
    # Ensure we're not in a transaction
    TransactionTestCase._reset_sequences(None, 'default')
    
    # Verify we're not in an atomic block
    assert not connection.in_atomic_block
    
    # Reset connection state
    connection.needs_rollback = False
    
    # Call set_rollback outside atomic block
    result = set_rollback()
    
    # Since we're not in an atomic block, needs_rollback should remain False
    # even though ATOMIC_REQUESTS is True
    assert not connection.in_atomic_block
    assert not connection.needs_rollback
    # Function should return None
    assert result is None

@pytest.mark.django_db(transaction=True)
def test_set_rollback_nested_transactions(settings):
    """Test set_rollback with nested atomic blocks."""
    from django.db import connections, transaction
    from rest_framework.views import set_rollback
    from django.test.testcases import TransactionTestCase
    
    # Configure atomic requests
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
    connection = connections['default']
    
    # Ensure we're not in a transaction
    TransactionTestCase._reset_sequences(None, 'default')
    
    # Verify initial state
    assert not connection.in_atomic_block
    assert not connection.needs_rollback
    
    # Start outer transaction
    with transaction.atomic():
        # Verify outer transaction state
        assert connection.in_atomic_block
        assert not connection.needs_rollback
        
        # Start inner transaction
        with transaction.atomic():
            # Call set_rollback in inner transaction
            result = set_rollback()
            # Verify rollback is needed within the inner transaction
            assert connection.needs_rollback
            # Verify set_rollback returns None
            assert result is None
            
            # We can still perform operations in the inner transaction
            # but they will be rolled back when the transaction ends
            
        # After inner transaction:
        # - We should still be in the outer transaction
        # - needs_rollback is reset when inner transaction ends
        assert connection.in_atomic_block
        # Django resets needs_rollback when exiting a transaction
        # This is expected behavior
        
    # After outer transaction:
    # - We should not be in a transaction
    # - Rollback flag should be cleared
    assert not connection.in_atomic_block
    assert not connection.needs_rollback

@pytest.mark.django_db(transaction=True)
def test_set_rollback_affects_current_transaction(settings):
    """Test that set_rollback only affects the current transaction."""
    from django.db import connections, transaction
    from rest_framework.views import set_rollback
    from django.test.testcases import TransactionTestCase
    
    # Configure atomic requests
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
    connection = connections['default']
    
    # Ensure we're not in a transaction
    TransactionTestCase._reset_sequences(None, 'default')
    
    # First transaction - set rollback
    with transaction.atomic():
        result = set_rollback()
        assert result is None  # set_rollback should return None
        assert connection.needs_rollback
    
    # After first transaction ends, needs_rollback should be reset
    assert not connection.needs_rollback
    
    # Second transaction - should start fresh
    with transaction.atomic():
        assert not connection.needs_rollback
        # Operations in this transaction should work normally

def test_exception_handler_returns_none_for_unknown_exception():
    """Test that exception_handler returns None for unknown exception types."""
    from rest_framework.views import exception_handler
    
    class CustomException(Exception):
        pass
    
    # Create a custom exception that isn't handled by DRF
    exc = CustomException("Custom error")
    context = {'view': None, 'args': (), 'kwargs': {}}
    
    # The handler should return None for unhandled exception types
    response = exception_handler(exc, context)
    assert response is None

def test_get_format_suffix_with_none_setting():
    """Test get_format_suffix when FORMAT_SUFFIX_KWARG is None."""
    class TestView(APIView):
        pass
    
    view = TestView()
    # Set FORMAT_SUFFIX_KWARG to None
    view.settings.FORMAT_SUFFIX_KWARG = None
    
    # Should return None when FORMAT_SUFFIX_KWARG is None
    result = view.get_format_suffix(format='json')
    assert result is None

def test_get_format_suffix_with_missing_kwarg():
    """Test get_format_suffix when the kwarg is not provided."""
    class TestView(APIView):
        pass
    
    view = TestView()
    # Set a format suffix kwarg
    view.settings.FORMAT_SUFFIX_KWARG = 'format'
    
    # Should return None when the kwarg is not in kwargs
    result = view.get_format_suffix(other_kwarg='value')
    assert result is None

def test_get_format_suffix_with_valid_kwarg():
    """Test get_format_suffix with a valid format suffix kwarg."""
    class TestView(APIView):
        pass
    
    view = TestView()
    # Set a format suffix kwarg
    view.settings.FORMAT_SUFFIX_KWARG = 'format'
    
    # Should return the format value when kwarg is present
    result = view.get_format_suffix(format='json')
    assert result == 'json'

def test_check_object_permissions_success():
    """Test check_object_permissions when all permissions pass."""
    from rest_framework.permissions import BasePermission
    
    class AllowObjectPermission(BasePermission):
        def has_object_permission(self, request, view, obj):
            return True
    
    class TestView(APIView):
        permission_classes = [AllowObjectPermission]
        
        def get(self, request, *args, **kwargs):
            return Response({'message': 'success'})
    
    # Create a test object
    test_obj = {'id': 1, 'name': 'test'}
    
    # Create a test request
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.request = request
    
    # This should not raise any exception
    try:
        view.check_object_permissions(request, test_obj)
    except Exception as e:
        pytest.fail(f"check_object_permissions raised an exception: {e}")

def test_check_object_permissions_multiple_permissions_success():
    """Test check_object_permissions with multiple permissions that all pass."""
    from rest_framework.permissions import BasePermission
    
    class FirstPermission(BasePermission):
        def has_object_permission(self, request, view, obj):
            return True
    
    class SecondPermission(BasePermission):
        def has_object_permission(self, request, view, obj):
            return True
    
    class TestView(APIView):
        permission_classes = [FirstPermission, SecondPermission]
        
        def get(self, request, *args, **kwargs):
            return Response({'message': 'success'})
    
    # Create a test object
    test_obj = {'id': 1, 'name': 'test'}
    
    # Create a test request
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.request = request
    
    # Should pass both permissions without raising an exception
    try:
        view.check_object_permissions(request, test_obj)
    except Exception as e:
        pytest.fail(f"check_object_permissions raised an exception: {e}")

def test_check_object_permissions_with_custom_attributes():
    """Test check_object_permissions with permissions that have custom message and code."""
    from rest_framework.permissions import BasePermission
    
    class CustomPermission(BasePermission):
        message = "Custom permission message"
        code = "custom_code"
        
        def has_object_permission(self, request, view, obj):
            return True
    
    class TestView(APIView):
        permission_classes = [CustomPermission]
        
        def get(self, request, *args, **kwargs):
            return Response({'message': 'success'})
    
    # Create a test object
    test_obj = {'id': 1, 'name': 'test'}
    
    # Create a test request
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.request = request
    
    # Should pass without raising an exception, even with custom attributes
    try:
        view.check_object_permissions(request, test_obj)
    except Exception as e:
        pytest.fail(f"check_object_permissions raised an exception: {e}")

def test_finalize_response_without_accepted_renderer():
    """Test finalize_response when request has no accepted_renderer."""
    class TestRenderer:
        media_type = 'application/test'
        def render(self, data, accepted_media_type=None, renderer_context=None):
            return data
    
    class TestView(APIView):
        renderer_classes = [TestRenderer]
        
        def get(self, request, *args, **kwargs):
            return Response({'message': 'test'})
    
    # Create request without accepted_renderer
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.format_kwarg = None
    view.headers = {}
    
    # Initialize request but don't perform content negotiation
    request = view.initialize_request(request)
    
    # Create response without performing content negotiation first
    response = Response({'message': 'test'})
    final_response = view.finalize_response(request, response)
    
    # Verify that accepted_renderer was set through forced negotiation
    assert hasattr(request, 'accepted_renderer')
    assert isinstance(request.accepted_renderer, TestRenderer)
    assert final_response.accepted_renderer == request.accepted_renderer
    assert final_response.accepted_media_type == 'application/test'

def test_finalize_response_vary_header_handling():
    """Test finalize_response handling of Vary headers."""
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({'message': 'test'})
    
    # Create request and response
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.format_kwarg = None
    
    # Set up headers with Vary
    view.headers = {
        'Vary': 'Accept-Language, Cookie',
        'Custom-Header': 'test-value'
    }
    
    # Initialize request and perform content negotiation
    request = view.initialize_request(request)
    neg = view.perform_content_negotiation(request)
    request.accepted_renderer, request.accepted_media_type = neg
    
    response = Response({'message': 'test'})
    final_response = view.finalize_response(request, response)
    
    # Verify Vary headers were properly handled
    assert 'vary' in final_response.headers
    vary_value = final_response.headers['vary']
    assert 'Accept-Language' in vary_value
    assert 'Cookie' in vary_value
    
    # Verify other headers were set
    assert final_response.headers['custom-header'] == 'test-value'

def test_finalize_response_multiple_vary_merging():
    """Test finalize_response merging multiple Vary headers."""
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            return Response({'message': 'test'})
    
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.format_kwarg = None
    
    # Set initial Vary header in response
    response = Response({'message': 'test'})
    response['Vary'] = 'Accept'
    
    # Set additional Vary headers in view
    view.headers = {
        'Vary': 'Accept-Language, Cookie',
        'Custom-Header': 'test-value'
    }
    
    # Initialize request and perform content negotiation
    request = view.initialize_request(request)
    neg = view.perform_content_negotiation(request)
    request.accepted_renderer, request.accepted_media_type = neg
    
    final_response = view.finalize_response(request, response)
    
    # Verify all Vary headers were merged
    assert 'vary' in final_response.headers
    vary_value = final_response.headers['vary']
    assert 'Accept' in vary_value
    assert 'Accept-Language' in vary_value
    assert 'Cookie' in vary_value

def test_finalize_response_non_drf_response():
    """Test finalize_response with non-DRF HttpResponse."""
    from django.http import HttpResponse
    
    class TestView(APIView):
        def get(self, request, *args, **kwargs):
            return HttpResponse('test')
    
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    view.format_kwarg = None
    view.headers = {
        'Custom-Header': 'test-value',
        'Vary': 'Accept-Language'
    }
    
    # Use regular HttpResponse
    response = HttpResponse('test')
    final_response = view.finalize_response(request, response)
    
    # Verify headers were added to HttpResponse
    assert final_response.headers['custom-header'] == 'test-value'
    assert 'Accept-Language' in final_response.headers['vary']

def test_handle_exception_not_authenticated_with_auth_header():
    """Test handle_exception with NotAuthenticated and WWW-Authenticate header."""
    class TestAuthenticator:
        def authenticate(self, request):
            return None
            
        def authenticate_header(self, request):
            return 'Bearer realm="api"'
    
    class TestView(APIView):
        authentication_classes = [TestAuthenticator]
        
        def get_exception_handler(self):
            return exception_handler
    
    # Create request and view
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    
    # Initialize request properly
    request = view.initialize_request(request)
    view.request = request
    
    # Raise NotAuthenticated
    exc = exceptions.NotAuthenticated()
    response = view.handle_exception(exc)
    
    # Should remain 401 due to auth header
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response['WWW-Authenticate'] == 'Bearer realm="api"'
    assert response.exception is True

def test_handle_exception_not_authenticated_without_auth_header():
    """Test handle_exception with NotAuthenticated and no WWW-Authenticate header."""
    class TestAuthenticator:
        def authenticate(self, request):
            return None
            
        def authenticate_header(self, request):
            return None
    
    class TestView(APIView):
        authentication_classes = [TestAuthenticator]
        
        def get_exception_handler(self):
            return exception_handler
    
    # Create request and view
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    
    # Initialize request properly
    request = view.initialize_request(request)
    view.request = request
    
    # Raise NotAuthenticated
    exc = exceptions.NotAuthenticated()
    response = view.handle_exception(exc)
    
    # Should be coerced to 403 due to no auth header
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'WWW-Authenticate' not in response
    assert response.exception is True

def test_handle_exception_authentication_failed_with_auth_header():
    """Test handle_exception with AuthenticationFailed and WWW-Authenticate header."""
    class TestAuthenticator:
        def authenticate(self, request):
            return None
            
        def authenticate_header(self, request):
            return 'Basic realm="api"'
    
    class TestView(APIView):
        authentication_classes = [TestAuthenticator]
        
        def get_exception_handler(self):
            return exception_handler
    
    # Create request and view
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    
    # Initialize request properly
    request = view.initialize_request(request)
    view.request = request
    
    # Raise AuthenticationFailed
    exc = exceptions.AuthenticationFailed("Invalid token")
    response = view.handle_exception(exc)
    
    # Should remain 401 due to auth header
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response['WWW-Authenticate'] == 'Basic realm="api"'
    assert response.exception is True

def test_handle_exception_authentication_failed_without_auth_header():
    """Test handle_exception with AuthenticationFailed and no WWW-Authenticate header."""
    class TestAuthenticator:
        def authenticate(self, request):
            return None
            
        def authenticate_header(self, request):
            return None
    
    class TestView(APIView):
        authentication_classes = [TestAuthenticator]
        
        def get_exception_handler(self):
            return exception_handler
    
    # Create request and view
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    
    # Initialize request properly
    request = view.initialize_request(request)
    view.request = request
    
    # Raise AuthenticationFailed
    exc = exceptions.AuthenticationFailed("Invalid token")
    response = view.handle_exception(exc)
    
    # Should be coerced to 403 due to no auth header
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'WWW-Authenticate' not in response
    assert response.exception is True

def test_handle_exception_authentication_failed_custom_status():
    """Test handle_exception preserves custom status code when auth header present."""
    class TestAuthenticator:
        def authenticate(self, request):
            return None
            
        def authenticate_header(self, request):
            return 'Bearer realm="api"'
    
    class TestView(APIView):
        authentication_classes = [TestAuthenticator]
        
        def get_exception_handler(self):
            return exception_handler
    
    # Create request and view
    factory = APIRequestFactory()
    request = factory.get('/')
    
    view = TestView()
    
    # Initialize request properly
    request = view.initialize_request(request)
    view.request = request
    
    # Raise AuthenticationFailed with custom status
    exc = exceptions.AuthenticationFailed()
    exc.status_code = status.HTTP_429_TOO_MANY_REQUESTS
    response = view.handle_exception(exc)
    
    # Should keep custom status code and add auth header
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response['WWW-Authenticate'] == 'Bearer realm="api"'
    assert response.exception is True

# Add this test to the existing SpeakerViewSet tests
def test_speaker_datetime_fields_in_api_response(self):
    """Test that created and updated fields are included in API responses"""
    speaker = baker.make('rw.Speaker', project=self.project)
    
    # Test GET endpoint includes datetime fields
    url = reverse('speaker-detail', args=[speaker.id])
    response = self.client.get(url)
    
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    data = response.json()
    
    self.assertIn('created', data)
    self.assertIn('updated', data)
    self.assertIsNotNone(data['created'])
    self.assertIsNotNone(data['updated'])

def test_speaker_color_fields_in_api_response(self):
    """Test that color fields are included in API responses"""
    speaker = baker.make('rw.Speaker', project=self.project)
    
    # Test GET endpoint includes color fields
    url = reverse('speaker-detail', args=[speaker.id])
    response = self.client.get(url)
    
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    data = response.json()
    
    self.assertIn('fill_color', data)
    self.assertIn('border_color', data)
    self.assertEqual(data['fill_color'], '#0000FF80')
    self.assertEqual(data['border_color'], '#0000FF')

def test_speaker_color_fields_can_be_updated(self):
    """Test that color fields can be updated via PATCH"""
    speaker = baker.make('rw.Speaker', project=self.project)
    
    # Test PATCH endpoint can update color fields
    url = reverse('speaker-detail', args=[speaker.id])
    patch_data = {
        'fill_color': '#FF000080',
        'border_color': '#FF0000'
    }
    response = self.client.patch(url, patch_data, content_type='application/json')
    
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    data = response.json()
    
    self.assertEqual(data['fill_color'], '#FF000080')
    self.assertEqual(data['border_color'], '#FF0000')
    
    # Verify database was updated
    speaker.refresh_from_db()
    self.assertEqual(speaker.fill_color, '#FF000080')
    self.assertEqual(speaker.border_color, '#FF0000')