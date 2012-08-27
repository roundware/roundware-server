from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from roundware.rw.admin import *
from roundware.rw.models import Project, Asset, Session, MasterUI
from guardian.shortcuts import assign
import sys

class FakeRequest():
    pass

def str_to_class(str):
    return getattr(sys.modules[__name__], str)

class TestAdmin(TestCase):
    """
    Test that the ProjectProtected helper classes prevent a user from viewing
    objects for which he does not have a access_project permission on the
    corresponding project.
    """

    def setUp(self):
        self.user = User.objects.create(username="user")
        self.user.set_password('password')
        self.user.is_staff = True
        self.site = AdminSite
        self.permitted_project = Project.objects.create(name="permitted", latitude=1, longitude=1,
            pub_date="1111-11-11", max_recording_length=1)
        self.excluded_project = Project.objects.create(name="excluded", latitude=1, longitude=1,
            pub_date="1111-11-11", max_recording_length=1)
        assign("access_project", self.user, self.permitted_project)
        self.user.save()
        self.request = FakeRequest()
        self.request.user = self.user

    def make_test_objects(self, model_class):
        pass

    def get_project_names(self, qs):
        pass

    def make_protected_test_objects_func(self, parent_class,
                                    permitted_parent, excluded_parent):
        def make_test_objects(model_class):
            permitted_object = model_class(**{parent_class: permitted_parent})
            excluded_object = model_class(**{parent_class: excluded_parent})
            return permitted_object, excluded_object

        return make_test_objects

    def _test_protected_model_admin(self, make_test_objects,
                                    get_project_names, test_data):
        """
        Test that objects are only accessible to a user if that user has
        permissions on the corresponding project.
        """
        for data_set in test_data:
            model_name = data_set[0]
            model_class = str_to_class(model_name)
            model_admin_class = str_to_class(model_name + "Admin")
            permitted_object, excluded_object = make_test_objects(model_class)

            # if the length of data_set is 2 the model has required fields
            if len(data_set) == 2:
                for field_data in data_set[1]:
                    field_name = field_data[0]
                    field_value = field_data[1]
                    setattr(excluded_object, field_name, field_value)
                    setattr(permitted_object, field_name, field_value)

            excluded_object.save()
            permitted_object.save()

            qs = model_admin_class(model_class, self.site).queryset(self.request)
            project_names = get_project_names(qs)
            print "model: " + model_name + "  project_names: ", project_names
            self.assertIn("permitted", project_names)
            self.assertNotIn("excluded", project_names)


    def test_protected_model_admin(self):
        """
        Test permissions on models that have a direct link to a project
        """
        protected_model_test_data = [
            ['Session', [['starttime', '1999-01-01']]],
            ['MasterUI', [['ui_mode_id', 123], ['tag_category_id', 1],
                ['select_id', 2], ['index', 3],
                ['min_volume', 3], ]],
            ['Audiotrack', [['minvolume', 1], ['maxvolume', 2],
                ['minduration', 3], ['maxduration', 4],
                ['mindeadair', 1], ['maxdeadair', 4],
                ['minfadeintime', 1], ['maxfadeintime', 2],
                ['minfadeouttime', 1], ['maxfadeouttime', 2],
                ['minpanpos', 1], ['maxpanpos', 2],
                ['minpanduration', 1], ['maxpanduration', 2]]],
            ['Speaker', [['latitude', 1], ['longitude', 2],
                ['mindistance', 1], ['maxdistance', 2],
                ['minvolume', 1], ['maxvolume', 2]]],
            ['Asset']
        ]

        make_test_objects = self.make_protected_test_objects_func('project',
                self.permitted_project, self.excluded_project)
        get_project_names = lambda qs: [q.project.name for q in qs]
        self._test_protected_model_admin(make_test_objects,
            get_project_names, protected_model_test_data)

    def test_protected_asset_model_admin(self):
        """
        Test permissions on models that have a link to a project through
        an asset object.
        """
        protected_asset_model_test_data = [
            ['Vote', [['session_id', 123]]],
            ['ListeningHistoryItem',[['session_id', 123],
                ['starttime', "1111-11-11"]]]
        ]

        permitted_asset = Asset.objects.create(project=self.permitted_project)
        excluded_asset = Asset.objects.create(project=self.excluded_project)

        make_test_objects = self.make_protected_test_objects_func('asset',
            permitted_asset, excluded_asset)
        get_project_names = lambda qs: [q.asset.project.name for q in qs]
        self._test_protected_model_admin(make_test_objects,
            get_project_names, protected_asset_model_test_data)

    def test_protected_session_model_admin(self):
        """
        Test permissions on models that have a link to a project through
        a session object.
        """
        protected_session_model_test_data = [
            ['Event', [['server_time', '1111-11-11']]],
            ['Envelope']
        ]

        extra_params = {'starttime' : '1111-11-11'}
        permitted_session = Session.objects.create(project=self.permitted_project,
            **extra_params)
        excluded_session = Session.objects.create(project=self.excluded_project,
            **extra_params)

        make_test_objects = self.make_protected_test_objects_func('session',
            permitted_session, excluded_session)
        get_project_names = lambda qs: [q.session.project.name for q in qs]
        self._test_protected_model_admin(make_test_objects,
            get_project_names, protected_session_model_test_data)


    def test_projected_ui_model_admin(self):
        """
        Test permission on models that have a link to a project through
        a MasterUI object.
        """
        protected_ui_model_data = [
            ['UIMapping',[['index', 1], ['tag_id', 1]]]
        ]

        extra_params = {
            'ui_mode_id' : 123,
            'tag_category_id' : 1,
            'select_id' : 2,
            'index' : 3
        }

        permitted_ui_master = MasterUI.objects.create(project=self.permitted_project, **extra_params)
        excluded_ui_master = MasterUI.objects.create(project=self.excluded_project,  **extra_params)

        make_test_objects = self.make_protected_test_objects_func('master_ui',
            permitted_ui_master, excluded_ui_master)
        get_project_names = lambda qs: [q.master_ui.project.name for q in qs]
        self._test_protected_model_admin(make_test_objects,
            get_project_names, protected_ui_model_data)

