# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from roundware.rw.models import (Asset, Event, Envelope, ListeningHistoryItem, Project,
                                 Session, Tag, TagRelationship, TagCategory,
                                 UIGroup, UIItem, UserProfile)
from roundware.api2 import serializers
from roundware.api2.filters import (EventFilterSet, AssetFilterSet, ListeningHistoryItemFilterSet,
                                    TagFilterSet, TagCategoryFilterSet, TagRelationshipFilterSet,
                                    UIGroupFilterSet, UIItemFilterSet)
from roundware.lib.api import (get_project_tags_new as get_project_tags, modify_stream, move_listener, heartbeat,
                               skip_ahead, pause, resume, add_asset_to_envelope, get_currently_streaming_asset,
                               save_asset_from_request, vote_asset, check_is_active,
                               vote_count_by_asset, log_event, play)
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.authtoken.models import Token
from rest_framework.decorators import detail_route, list_route
import logging
from random import sample

logger = logging.getLogger(__name__)


# Note: Keep this stuff in alphabetical order!


class AssetViewSet(viewsets.ViewSet):
    """
    API V2: api/2/assets/
            api/2/assets/:asset_id/
    """

    # TODO: Implement DjangoObjectPermissions
    queryset = Asset.objects.all()
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        """
        GET api/2/assets/:id/ - Get asset by id
        """
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            raise Http404("Asset not found")
        serializer = serializers.AssetSerializer(asset)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/assets/ - Create a new asset
        """
        if "session_id" not in request.data:
            raise ParseError("session_id required")

        try:
            session_id = int(request.data["session_id"])
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            raise Http404("Session not found")

        if "asset_id" not in request.data and "file" not in request.data:
            raise ParseError("Must supply either asset_id or file")

        asset = None
        if "asset_id" in request.data:
            try:
                asset_id = int(request.data["asset_id"])
                asset = Asset.objects.get(pk=asset_id)
            except ValueError, Asset.DoesNotExist:
                raise Http404("Asset with id %s not found" % request.data["asset_id"])
        asset = save_asset_from_request(request, session, asset)
        serializer = serializers.AssetSerializer(asset)
        return Response(serializer.data)

    def list(self, request):
        """
        GET api/2/assets/ - retrieve list of assets filtered by parameters
        """
        assets = AssetFilterSet(request.query_params)
        serializer = serializers.AssetSerializer(assets, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post', 'get'])
    def votes(self, request, pk=None):
        if request.method == "POST":
            vote_op = vote_asset(request, asset_id=pk)
            vote = vote_op["vote"]
            serializer = serializers.VoteSerializer(vote)
            return Response(serializer.data)
        else:
            count = vote_count_by_asset(pk)
            return Response(count)

    @list_route(methods=['get'])
    def random(self, request, pk=None):
        """
        GET api/2/assets/random/ - retrieve random list of assets filtered by parameters
        """
        assets = AssetFilterSet(request.query_params).qs.values_list('id', flat=True)
        asset_count = len(assets)
        if asset_count is 0:
            return Response([])
        # ensure limit isn't greater than asset_count which causes sample to fail
        limit = min(int(request.query_params.get('limit', 1)), asset_count)
        # ensure indices returned are unique
        random_idx = sample(range(asset_count), limit)
        selected_ids = [assets[x] for x in random_idx]
        results = Asset.objects.filter(id__in=selected_ids)
        serializer = serializers.AssetSerializer(results, many=True)
        return Response(serializer.data)


class EnvelopeViewSet(viewsets.ViewSet):
    """
    API V2: api/2/envelopes/
            api/2/envelopes/:envelope_id/
    """
    queryset = Envelope.objects.all()

    def create(self, request):
        """
        POST api/2/envelopes/ - Creates a new envelope based on passed session_id
        """
        serializer = serializers.EnvelopeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def partial_update(self, request, pk=None):
        """
        PATCH api/2/envelopes/:id/ - Adds an asset to the envelope
        """
        if "asset_id" in request.data or "file" in request.FILES:
            try:
                result = add_asset_to_envelope(request, envelope_id=pk)
            except Exception as e:
                return Response({"detail": str(e)}, status.HTTP_400_BAD_REQUEST)
            asset_obj = Asset.objects.get(pk=result['asset_id'])
            serializer = serializers.AssetSerializer(asset_obj)
            return Response(serializer.data)
        else:
            raise ParseError("asset_id or file required")


class EventViewSet(viewsets.ViewSet):
    """
    API V2: api/2/events/
            api/2/events/:event_id/
    """

    # TODO: Implement ViewCreate permission.
    queryset = Event.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/events/ - Provides list of events filtered by parameters
        """
        events = EventFilterSet(request.query_params)
        serializer = serializers.EventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/events/:event_id/ - Get event by id
        """
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404("Event not found")
        serializer = serializers.EventSerializer(event)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/events/ - Create a new event
        """
        if 'session_id' not in request.data:
            raise ParseError("a session_id is required for this operation")
        if 'event_type' not in request.data:
            raise ParseError("an event_type is required for this operation")
        try:
            e = log_event(request.data['event_type'], request.data['session_id'], request.data)
        except Exception as e:
            raise ParseError(str(e))
        serializer = serializers.EventSerializer(e)
        return Response(serializer.data)


class ListenEventViewSet(viewsets.ViewSet):
    """
    API V2: api/2/listenevents/
            api/2/listenevents/:id/
    """

    # TODO: Rename ListeningHistoryItem model to ListenEvent.
    queryset = ListeningHistoryItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/listenevents/ - Get listenevents by filtering parameters
        """
        events = ListeningHistoryItemFilterSet(request.query_params)
        serializer = serializers.ListenEventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/listenevents/:event_id/ - Get listenevent by id
        """
        try:
            event = ListeningHistoryItem.objects.get(pk=pk)
        except ListeningHistoryItem.DoesNotExist:
            raise Http404("ListenEvent not found")
        serializer = serializers.ListenEventSerializer(event)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ViewSet):
    """
    API V2: api/2/projects/:project_id
            api/2/projects/:project_id/tags
    """
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        if "session_id" in request.query_params:
            session = get_object_or_404(Session, pk=request.query_params["session_id"])
            project = get_object_or_404(Project, pk=pk)
            serializer = serializers.ProjectSerializer(project,
                                                       context={"session": session,
                                                                "admin": "admin" in request.query_params})
        else:
            raise ParseError("session_id parameter is required")
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        session = None
        if "session_id" in request.query_params:
            session = get_object_or_404(Session, pk=request.query_params["session_id"])

        tags = get_project_tags(p=pk)
        serializer = serializers.TagSerializer(tags, context={"session": session,
                                                              "admin": "admin" in request.query_params}, many=True)
        return Response({"tags": serializer.data})

    @detail_route(methods=['get'])
    def uigroups(self, request, pk=None):
        params = request.query_params.copy()
        params["project_id"] = pk
        uigroups = UIGroupFilterSet(params)
        serializer = serializers.UIGroupSerializer(uigroups,
                                                   context={"admin": "admin" in request.query_params},
                                                   many=True)
        return Response({"ui_groups": serializer.data})

    @detail_route(methods=['get'])
    def assets(self, request, pk=None):
        params = request.query_params.copy()
        params["project_id"] = pk
        assets = AssetFilterSet(params)
        # serialize and return
        serializer = serializers.AssetSerializer(assets, context={"admin": "admin" in request.query_params}, many=True)
        return Response(serializer.data)


class SessionViewSet(viewsets.ViewSet):
    """
    API V2: api/2/sessions/
    """
    queryset = Session.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        # check if geo_listen_enabled is passed in request.data and if not,
        # add it with value from project.geo_listen_enabled
        if 'geo_listen_enabled' not in request.data:
            p = Project.objects.get(id=request.data['project_id'])
            request.data['geo_listen_enabled'] = p.geo_listen_enabled
            logger.info('geo_listen_enabled not passed! set to project value: %s' % request.data['geo_listen_enabled'])
        serializer = serializers.SessionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamViewSet(viewsets.ViewSet):
    """
    The primary communication channel for handling the Roundware audio stream.
    API V2: api/2/streams/
            api/2/streams/:id/
    """
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        serializer = serializers.StreamSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            raise ParseError(serializer.errors)
        return Response(serializer.save())

    def partial_update(self, request, pk=None):
        try:
            if "tag_ids" in request.data:
                success = modify_stream(request, context={"pk": pk})
            elif "longitude" in request.data and "latitude" in request.data:
                success = move_listener(request, context={"pk": pk})
            else:
                raise ParseError("must supply something to update")
            if success["success"]:
                return Response()
            else:
                return Response({"detail": success["error"]},
                                status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "could not update stream: %s" % e},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def heartbeat(self, request, pk=None):
        try:
            heartbeat(request, session_id=pk)
            return Response()
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def playasset(self, request, pk=None):
        try:
            return Response(play({
                'session_id': pk,
                'asset_id': request.POST.get('asset_id')
            }))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def skip(self, request, pk=None):
        try:
            return Response(skip_ahead(request, session_id=pk))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def pause(self, request, pk=None):
        try:
            return Response(pause(request, session_id=pk))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def resume(self, request, pk=None):
        try:
            return Response(resume(request, session_id=pk))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def replayasset(self, request, pk=None):
        try:
            result = get_currently_streaming_asset(request, session_id=pk)
            return Response(play({
                'session_id': pk,
                'asset_id': str(result.get('asset_id'))
            }))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def isactive(self, request, pk=None):
        try:
            result = check_is_active(pk)
            stream_id = int(pk)
            return Response({
                'stream_id': stream_id,
                'active': result
            })
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ViewSet):
    """
    API V2: api/2/tags/
            api/2/tags/:tag_id/
    """
    # TODO: Return messages and relationships in response
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/tags/ - Provides list of tag filtered by parameters
        """
        tags = TagFilterSet(request.query_params)
        serializer = serializers.TagSerializer(tags, many=True)
        return Response({"tags": serializer.data})

    def retrieve(self, request, pk=None):
        """
        GET api/2/tags/:id/ - Get tag by id
        """
        try:
            tag = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            raise Http404("Tag not found")
        session = None
        if "session_id" in request.query_params:
            try:
                session = Session.objects.get(pk=request.query_params["session_id"])
            except:
                raise ParseError("Session not found")
        serializer = serializers.TagSerializer(tag, context={"session": session})
        return Response(serializer.data)


class TagCategoryViewSet(viewsets.ViewSet):
    """
    API V2: api/2/tagcategories/
            api/2/tagcategories/:id/
    """
    queryset = TagCategory.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return TagCategory.objects.get(pk=pk)
        except Tag.DoesNotExist:
            raise Http404("TagCategory not found")

    def list(self, request):
        """
        GET api/2/tagcategories/ - Provides list of TagCategories filtered by parameters
        """
        tagcategories = TagCategoryFilterSet(request.query_params)
        serializer = serializers.TagCategorySerializer(tagcategories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/tagcategories/:id/ - Get TagCategory by id
        """
        tagcategory = self.get_object(pk);
        serializer = serializers.TagCategorySerializer(tagcategory)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/tagcategories/ - Create a new TagCategory
        """
        serializer = serializers.TagCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def partial_update(self, request, pk):
        """
        PATCH api/2/tagcategories/:id/ - Update existing TagCategory
        """
        tagcategory = self.get_object(pk);
        serializer = serializers.TagCategorySerializer(tagcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/tagcategories/:id/ - Delete a TagCategory
        """
        tagcategory = self.get_object(pk);
        tagcategory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagRelationshipViewSet(viewsets.ViewSet):
    """
    API V2: api/2/tagrelationships/
            api/2/tagrelationships/:id/
    """
    queryset = TagRelationship.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/tagrelationships/ - Provides list of TagRelationships filtered by parameters
        """
        tagrelationships = TagRelationshipFilterSet(request.query_params)
        serializer = serializers.TagRelationshipSerializer(tagrelationships, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/tagrelationships/:id/ - Get TagRelationship by id
        """
        try:
            tagrelationship = TagRelationship.objects.get(pk=pk)
        except TagRelationship.DoesNotExist:
            raise Http404("TagRelationship not found")
        # session_id not needed, because no localization..?
        serializer = serializers.TagRelationshipSerializer(tagrelationship)
        return Response(serializer.data)


class UIGroupViewSet(viewsets.ViewSet):
    """
    API V2: api/2/uigroups/
            api/2/uigroups/:uigroup_id/
    """
    queryset = UIGroup.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/uigroups/ - Provides list of uigroups filtered by parameters
        """
        uigroups = UIGroupFilterSet(request.query_params)
        serializer = serializers.UIGroupSerializer(uigroups, many=True)
        return Response({"ui_groups": serializer.data})

    def retrieve(self, request, pk=None):
        """
        GET api/2/uigroups/:id/ - Get uigroup by id
        """
        try:
            uigroup = UIGroup.objects.get(pk=pk)
        except UIGroup.DoesNotExist:
            raise Http404("UIGroup not found")
        session = None
        if "session_id" in request.query_params:
            try:
                session = Session.objects.get(pk=request.query_params["session_id"])
            except:
                raise ParseError("Session not found")
        serializer = serializers.UIGroupSerializer(uigroup, context={"session": session})
        return Response(serializer.data)


class UIItemViewSet(viewsets.ViewSet):
    """
    API V2: api/2/uiitems/
            api/2/uiitems/:uiitem_id/
    """
    queryset = UIItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/uiitems/ - Provides list of uiitems filtered by parameters
        """
        uiitems = UIItemFilterSet(request.query_params)
        serializer = serializers.UIItemSerializer(uiitems, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/uiitems/:id/ - Get uiitem by id
        """
        try:
            uiitem = UIItem.objects.get(pk=pk)
        except UIItem.DoesNotExist:
            raise Http404("UIItem not found")
        # session_id not needed, because no localization..?
        serializer = serializers.UIItemSerializer(uiitem)
        return Response(serializer.data)


class UserViewSet(viewsets.ViewSet):
    """
    API V2: api/2/users/
    """
    queryset = User.objects.all()

    def create(self, request):
        """
        POST api/2/user/ - Creates new user based on either device_id or username/pass. Returns token
        """
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            # try to find user profile:
            try:
                profile = UserProfile.objects.get(device_id=self.request.data["device_id"][:254])
                user = profile.user
                # try to find existing token
                try:
                    token = Token.objects.get(user=profile.user)
                # create a token for this profile
                except Token.DoesNotExist:
                    token = Token.objects.create(user=profile.user)
            # no matching device_id in profiles, create new user
            except UserProfile.DoesNotExist:
                # save the serializer to create new user account
                user = serializer.save()
                # obtain token for this new user
                token = Token.objects.create(user=user)
        return Response({"username": user.username, "token": token.key})
