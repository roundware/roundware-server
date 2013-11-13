from django.test import TestCase

from model_mommy import mommy

from roundware.rw import models


class TestMasterUI(TestCase):
    """ exercise MasterUI model class """

    def setUp(self):
        # make masterui, makes our tagcategory, uimode, project, 
        # selectionmethod
        self.masterui = mommy.make('rw.MasterUI')
        self.other_uimode = mommy.make('rw.UIMode')
        self.project = self.masterui.project

    def test_tag_category_invalidation_post_save(self):
        """ test that cached value for tag categories for the MasterUI's mode
        is invalidated after MasterUI saved.
        """
        ui_mode_name = self.masterui.ui_mode.name
        orig_ui_mode_name = ui_mode_name        
        get_orig_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode_name)

        # is original tag_cat of masterui returned by Project's method
        self.assertIn(self.masterui.tag_category, get_orig_tag_cats)

        # change the ui mode of our masterui
        self.masterui.ui_mode = self.other_uimode

        # should still get old tag categories... cached
        get_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode_name)
        self.assertIn(self.masterui.tag_category, get_tag_cats)

        # save the masterui, now should not get old tag categories... 
        # cached copy invalidated
        self.masterui.save()
        get_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode_name)
        self.assertNotIn(self.masterui.tag_category, get_tag_cats)


class TestProject(TestCase):

    def setUp(self):
        self.project = mommy.make('rw.Project')
        self.ui_mode = mommy.make('rw.UIMode')

    def test_no_tag_cats_returned_new_project(self):
        """ test no tag_categories returned for a new project with no masterui
        """
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode.name)
        self.assertTrue(len(cats) == 0)

    def test_correct_tag_cats_returned(self):
        """ test that we get correct tagcategories for our project once
            we add a MasterUI.
        """
        masterui = mommy.make('rw.MasterUI', project=self.project, 
                              ui_mode=self.ui_mode)
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode.name)
        self.assertIn(masterui.tag_category, cats)

    def test_no_tag_cats_returned_wrong_uimode(self):
        """ test no tag_categories returned if we specify a uimode that 
            is not connected to project via a MasterUI
        """
        other_ui_mode = mommy.make('rw.UIMode', name='bogus')
        other_master_ui = mommy.make('rw.MasterUI', project=self.project,
                                     ui_mode=other_ui_mode)
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode.name)
        self.assertNotIn(other_master_ui.tag_category, cats)
