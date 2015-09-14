# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import sys

from django.test.client import Client
from django.contrib.admin.sites import AdminSite

from django_webtest import WebTest

from roundware.rw.admin import *
from roundware.rw.models import Project, Asset, Session, MasterUI
from roundware.settings import DEFAULT_SESSION_ID
from guardian.shortcuts import assign
from model_mommy import mommy

from .common import FakeRequest, RWTestCase


def str_to_class(string):
    # print __name__
    return getattr(sys.modules[__name__], string)


class TestAssetAdmin(RWTestCase, WebTest):

    def setUp(self):
        super(type(self), TestAssetAdmin).setUp(self)
        self.client = Client()
        self.user = mommy.make_recipe('rw.basic_user', is_staff=True,
                                      is_superuser=True)
        self.user.set_password('foo')
        self.user.save()
        self.username = self.user.username
        self.session1 = mommy.make('rw.Session', id=DEFAULT_SESSION_ID)
        self.tagcat1 = mommy.make(TagCategory, name='tagcat1')
        self.tagcat2 = mommy.make(TagCategory, name='tagcat2')
        self.tagcat3 = mommy.make(TagCategory, name='tagcat3')
        self.tag1 = mommy.make(Tag, tag_category=self.tagcat1,
                               description='tag1')
        self.tag2 = mommy.make(Tag, tag_category=self.tagcat2,
                               description='tag2')
        self.asset1 = mommy.make(Asset, id=1989081234, tags=[self.tag1],
                                 audiolength=10)
        self.asset2 = mommy.make(Asset, id=2987123432, tags=[self.tag2],
                                 audiolength=50000000000)
        self.asset3 = mommy.make(Asset, id=312343214134, tags=[],
                                 audiolength=60000000001)

    def _login(self, username, password):
        form = self.app.get('/admin').follow().form
        form['username'] = username
        form['password'] = password
        return form.submit()

    def need_updating_for_boostrapped_test_func_filter_by_alpha_tag_cat_show_correct_filters(self):
        """ test that custom filter providing alphabetized filters by 
        tag category are available, based on tags on assets
        """
        self._login(username=self.username, password='foo')
        response = self.app.get('/admin/rw/asset', user=self.username).follow()
        lxml = response.lxml
        self.assertEqual(200, response.status_int)
        # first should get a list of categories
        self.assertEqual("All Categories", lxml.xpath("(//ul[@class='dropdown-menu']/li[@class='nav-header'][contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[1]/a")[0].text)
        self.assertEqual("?", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[1]/a/@href")[0])
        self.assertEqual("All", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[2]/a")[0].text)
        self.assertEqual("tagcat1", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[3]/a")[0].text)
        self.assertEqual("tagcat2", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[4]/a")[0].text)
        # clicking into one of the categories will load a page
        # wher categories are replaced by tags in that tagcategory
        response2 = response.click('tagcat1')
        lxml = response2.lxml
        self.assertEqual("All Categories", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[1]/a")[0].text)
        self.assertEqual("?", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[1]/a/@href")[0])
        self.assertEqual("All", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[2]/a")[0].text)
        self.assertEqual("?tags__tag_category__name__iexact=tagcat1", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[2]/a/@href")[0])
        self.assertEqual("tag1", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[3]/a")[0].text)
        self.assertEqual("?tags__description=tag1&tags__tag_category__name__iexact=tagcat1", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By tag category')]/following-sibling::ul)[1]/li[3]/a/@href")[0])
        self.assertIn(str(self.asset1.id), response2.text)
        self.assertNotIn(str(self.asset2.id), response2.text)
        response3 = response2.click('tag1')
        self.assertIn(str(self.asset1.id), response3.text)
        self.assertNotIn(str(self.asset2.id), response3.text)

    def need_updating_for_boostrapped_test_func_filter_by_audiolength_show_correct_filters(self):
        """ test we get custom filter providing filters by range of
        audiolengths on assets
        """
        self._login(username=self.username, password='foo')
        response = self.app.get('/admin/rw/asset', user=self.username).follow()
        lxml = response.lxml
        self.assertEqual(200, response.status_int)
        self.assertEqual("Any", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[1]/a")[0].text)
        self.assertEqual("< 10s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[2]/a")[0].text)
        self.assertEqual("10s - 20s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[3]/a")[0].text)
        self.assertEqual("20s - 30s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[4]/a")[0].text)
        self.assertEqual("30s - 40s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[5]/a")[0].text)
        self.assertEqual("40s - 50s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[6]/a")[0].text)
        self.assertEqual("50s - 60s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[7]/a")[0].text)
        self.assertEqual("> 60s", lxml.xpath("(//div[@id='changelist-filter']/h3[contains(text(), 'By audio file length')]/following-sibling::ul)[1]/li[8]/a")[0].text)

    def need_updating_for_boostrapped_test_func_filter_by_audiolength_filter_correctly(self):
        """ test that custom audiolength filter works correctly to filter
        the assets
        """
        self._login(username=self.username, password='foo')
        response = self.app.get('/admin/rw/asset', user=self.username).follow()
        self.assertEqual(200, response.status_int)
        html = response.click('&lt; 10s').text
        self.assertIn(str(self.asset1.id), html)
        self.assertNotIn(str(self.asset2.id), html)
        self.assertNotIn(str(self.asset3.id), html)
        html = response.click('50s - 60s').text
        self.assertNotIn(str(self.asset1.id), html)
        self.assertIn(str(self.asset2.id), html)
        self.assertNotIn(str(self.asset3.id), html)
        html = response.click('&gt; 60s').text
        self.assertNotIn(str(self.asset1.id), html)
        self.assertNotIn(str(self.asset2.id), html)
        self.assertIn(str(self.asset3.id), html)


class TestProtectedAdmin(RWTestCase):

    """
    Test that the ProjectProtected helper classes prevent a user from viewing
    objects for which he does not have a access_project permission on the
    corresponding project.
    """

    def setUp(self):
        super(type(self), TestProtectedAdmin).setUp(self)

        self.user = mommy.make_recipe('rw.basic_user', is_staff=True)
        # self.user.is_staff = True
        self.site = AdminSite
        self.permitted_project = mommy.make('rw.Project', name='permitted')
        self.excluded_project = mommy.make('rw.Project', name='excluded')
        self.ui_mode = MasterUI.LISTEN
        self.default_session = mommy.make_recipe('rw.default_session')
        self.default_session_id = self.default_session.id
        self.tag_category = mommy.make('rw.TagCategory')
        self.tag = mommy.make('rw.Tag')
        self.selection_method = MasterUI.SINGLE
        # self.permitted_project = Project.objects.create(name="permitted", latitude=1, longitude=1,
        #     pub_date="1111-11-11", max_recording_length=1)
        # self.excluded_project = Project.objects.create(name="excluded", latitude=1, longitude=1,
        #     pub_date="1111-11-11", max_recording_length=1)
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

            qs = model_admin_class(model_class, self.site).get_queryset(self.request)
            project_names = get_project_names(qs)
            # print "model: " + model_name + "  project_names: ", project_names
            self.assertIn("permitted", project_names)
            self.assertNotIn("excluded", project_names)

    def test_protected_model_admin(self):
        """
        Test permissions on models that have a direct link to a project
        """
        protected_model_test_data = [
            ['Session', [['starttime', '1999-01-01']]],
            ['MasterUI', [['ui_mode', self.ui_mode],
                          ['tag_category_id', self.tag_category.id],
                          ['select', self.selection_method],
                          ['index', 3],
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
            ['Vote', [['session_id', self.default_session_id]]],
            ['ListeningHistoryItem', [['session_id', self.default_session_id],
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

        extra_params = {'starttime': '1111-11-11'}
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
            ['UIMapping', [['index', 1], ['tag_id', self.tag.id]]]
        ]

        extra_params = {
            'ui_mode': self.ui_mode,
            'tag_category_id': self.tag_category.id,
            'select': self.selection_method,
            'index': 3
        }

        permitted_ui_master = MasterUI.objects.create(project=self.permitted_project, **extra_params)
        excluded_ui_master = MasterUI.objects.create(project=self.excluded_project, **extra_params)

        make_test_objects = self.make_protected_test_objects_func('master_ui',
                                                                  permitted_ui_master, excluded_ui_master)
        get_project_names = lambda qs: [q.master_ui.project.name for q in qs]
        self._test_protected_model_admin(make_test_objects,
                                         get_project_names, protected_ui_model_data)
