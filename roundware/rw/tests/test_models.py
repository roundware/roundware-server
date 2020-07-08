# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from model_bakery import baker

from roundware.rw import models
from roundware.settings import DEFAULT_SESSION_ID

from rw.tests.common import use_locmemcache, RWTestCase


class TestUIGroup(RWTestCase):

    """ exercise UIGroup model class """

    def setUp(self):
        super(type(self), TestUIGroup).setUp(self)

        # make uigroup, makes our tagcategory, uimode, project,
        # selectionmethod
        self.uigroup = baker.make('rw.UIGroup')
        self.other_uimode = models.UIGroup.SPEAK
        self.project = self.uigroup.project

    @use_locmemcache(models, 'cache')
    def test_tag_category_cache_invalidation_post_save(self):
        """ test that cached value for tag categories for the UIGroup's mode
        is invalidated after UIGroup saved.
        """
        ui_mode = self.uigroup.ui_mode
        get_orig_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode)

        # is original tag_cat of uigroup returned by Project's method
        self.assertIn(self.uigroup.tag_category, get_orig_tag_cats)

        # change the ui mode of our uigroup
        self.uigroup.ui_mode = self.other_uimode

        # should still get old tag categories... cached
        get_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode)
        self.assertIn(self.uigroup.tag_category, get_tag_cats)

        # save the uigroup, now should not get old tag categories...
        # cached copy invalidated
        self.uigroup.save()
        get_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode)
        self.assertNotIn(self.uigroup.tag_category, get_tag_cats)


class TestProject(RWTestCase):

    def setUp(self):
        super(type(self), TestProject).setUp(self)
        self.project = baker.make('rw.Project')
        self.ui_mode = models.UIGroup.LISTEN

    def test_no_tag_cats_returned_new_project(self):
        """ test no tag_categories returned for a new project with no uigroup
        """
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode)
        self.assertTrue(len(cats) == 0)

    def test_correct_tag_cats_returned(self):
        """ test that we get correct tagcategories for our project once
            we add a UIGroup.
        """
        uigroup = baker.make('rw.UIGroup', project=self.project,
                              ui_mode=self.ui_mode)
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode)
        self.assertIn(uigroup.tag_category, cats)

    def test_no_tag_cats_returned_wrong_uimode(self):
        """ test no tag_categories returned if we specify a uimode that
            is not connected to project via a UIGroup
        """
        other_ui_group = baker.make('rw.UIGroup', project=self.project,
                                     ui_mode=models.UIGroup.SPEAK)
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode)
        self.assertNotIn(other_ui_group.tag_category, cats)


class TestAsset(RWTestCase):

    def setUp(self):
        super(type(self), TestAsset).setUp(self)

        self.session1 = baker.make('rw.Session')
        self.session2 = baker.make('rw.Session')
        self.project = baker.make('rw.Project')
        self.asset1 = baker.make('rw.Asset')
        self.asset2 = baker.make('rw.Asset')
        self.vote1 = baker.make('rw.Vote', session=self.session1,
                                asset=self.asset1, type="like")
        self.vote2 = baker.make('rw.Vote', session=self.session2,
                                asset=self.asset1, type="like")
        self.vote3 = baker.make('rw.Vote', session=self.session1,
                                asset=self.asset2, type="like")
        self.vote4 = baker.make('rw.Vote', session=self.session1,
                                asset=self.asset1, type="flag")

    def test_get_likes(self):
        self.assertEquals(2, self.asset1.get_likes())
        self.assertEquals(1, self.asset2.get_likes())

    def test_get_flags(self):
        self.assertEquals(1, self.asset1.get_flags())

    def test_distance(self):
        distance = self.asset1.distance({'latitude': 0, 'longitude': 0})
