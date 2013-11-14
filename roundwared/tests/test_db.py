from django.test import TestCase

from model_mommy import mommy

# from .common import *
from roundware.rw.models import (MasterUI, Language, Session, 
                                 UIMapping, Project, LocalizedString, Tag)
from roundwared.db import get_config_tag_json


class TestGetConfigTagJSON(TestCase):
    """ test various permutations of db.get_config_tag_json 
    """

    def setUp(self):
        self.maxDiff = None

        # make a masterui, a project, a ui_mode, tag category, selectionmethod
        self.english = mommy.make(Language, language_code='en')
        self.spanish = mommy.make(Language, language_code='es')
        self.english_hdr = mommy.make(LocalizedString, 
                                      localized_string="Head",
                                      language=self.english)
        self.spanish_hdr = mommy.make(LocalizedString, 
                                      localized_string="Cabeza",
                                      language=self.spanish)
        self.masterui = mommy.make(MasterUI, active=True, 
                                   tag_category__name='TagCatName',
                                   index=1,
                                   header_text_loc=[self.english_hdr,
                                                    self.spanish_hdr])
        self.ui_mode_one = self.masterui.ui_mode

        self.english_sess = mommy.make(Session, project=self.masterui.project,
                                       language=self.english)
        self.spanish_sess = mommy.make(Session, project=self.masterui.project,
                                       language=self.spanish)
        self.english_msg = mommy.make(LocalizedString, localized_string="One",
                                      language=self.english)
        self.spanish_msg = mommy.make(LocalizedString, localized_string="Uno",
                                      language=self.spanish)
        self.project_one = self.masterui.project
        self.tag = mommy.make(Tag, data="{'json':'value'}",
                              loc_msg=[self.english_msg, self.spanish_msg])
        self.ui_mapping_one = mommy.make(UIMapping, master_ui=self.masterui,
                                         active=True, tag=self.tag,
                                         index=1, default=True)
        self.master_ui_two = mommy.make(MasterUI, name='inactivemui', 
                                        ui_mode=self.ui_mode_one, active=True)
        self.project_two = self.master_ui_two.project  
        self.project_three = mommy.make(Project, name='project_three')

    def test_get_uimapping_info_for_project(self):
        """ Test proper UIMapping data returned based on project passed """
        config = get_config_tag_json(self.project_one, self.english_sess)
        expected = {self.ui_mode_one.name: [ 
            {'name': self.masterui.name, 
             'header_text': "Head", 
             'code': 'TagCatName',
             'select': self.masterui.select.name, 
             'order': 1,
             'defaults': [self.ui_mapping_one.tag.id],
             'options': [{
                 'tag_id': self.ui_mapping_one.tag.id, 
                 'order': 1, 
                 'data': "{'json':'value'}",
                 'relationships': [],
                 'value': 'One'
             }]},
        ]}
        self.assertEquals(expected, config)

    def test_only_masteruis_for_project_returned(self):
        """ Confirm only info for MasterUIs for passed project or session
            project are returned in config tag dictionary
        """
        config = get_config_tag_json(self.project_three)
        self.assertEquals({}, config)

        config = get_config_tag_json(self.project_two)
        # should not have any uimapping info for project _one_
        self.assertNotIn(self.masterui.name, 
                         [dic['name'] for dic in 
                          config[self.ui_mode_one.name]])

    def test_session_project_overrides_passed_project(self):
        """ The project associated with a passed session should be used 
            even if a project is explicitly passed. (really?)
        """
        pass

    def test_only_active_masteruis_returned(self):
        """ Confirm that only active MasterUIs are returned in 
            config tag 'JSON' (dictionary)
        """
        pass

    def test_get_right_masterui_without_passed_project(self):
        """ Don't pass a project, just use the project for the session.
            Do we still get the right MasterUI?
        """
        pass

    def test_get_correct_localized_header_text(self):
        """ Test that we get correct localized header text for session, or if 
            none passed, header text in English.
        """
        pass

    def test_tag_values_correctly_localized(self):
        """ Test that we get correct localized header text for tag values
            based on session language, or if none passed, in English.
        """
        pass

    def test_default_UIMappings_returned_as_default(self):
        """ Test that dictionary key for default has correct default 
            UIMappings.
        """
        pass
