from __future__ import unicode_literals
import datetime
from model_mommy import mommy

from .common import RoundwaredTestCase
from roundware.rw.models import (MasterUI, Session, Tag, Asset, TagCategory,
                                 UIMapping, Project, LocalizedString,
                                 ListeningHistoryItem)
from roundwared.db import (get_config_tag_json, filter_recs_for_tags,
                           get_recordings, get_current_streaming_asset,
                           cleanup_history_for_session, get_default_tags_for_project)
from roundwared.roundexception import RoundException


class TestGetRecordings(RoundwaredTestCase):

    """ test various permutations of db.get_recordings
    """

    def setUp(self):
        super(type(self), TestGetRecordings).setUp(self)

        self.project1 = mommy.make(Project, name='Project One')
        self.project2 = mommy.make(Project, name='Project Two')
        self.session1 = mommy.make(Session, project=self.project1,
                                   language=self.english)
        self.session2 = mommy.make(Session, project=self.project2,
                                   language=self.english)
        self.tagcat2 = mommy.make(TagCategory)
        self.tagcat3 = mommy.make(TagCategory)
        self.tag2 = mommy.make(Tag, tag_category=self.tagcat2, value='tag2')
        self.tag3 = mommy.make(Tag, tag_category=self.tagcat3, value='tag3')
        self.masterui1 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat1)
        self.masterui2 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat2)
        self.masterui2 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat3)
        self.masterui4 = mommy.make(MasterUI, project=self.project2,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat2)
        # Add one default tag to project1
        self.uimapping1 = mommy.make(UIMapping, master_ui=self.masterui1,
                                     tag=self.tag1, default=True, active=True)
        self.asset1 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000)
        self.asset2 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000)
        self.asset3 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag2, self.tag1],
                                 audiolength=2000)
        self.asset4 = mommy.make(Asset, project=self.project2,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000)


    def test_get_default_tags_for_project(self):
        """ Project1 has one default tag, Project2 has no default tags.
        """
        default_tags = get_default_tags_for_project(self.project1)
        self.assertEqual(default_tags, [self.tag1.id])

        default_tags = get_default_tags_for_project(self.project2)
        self.assertEqual(default_tags, [])

    def test_correct_assets_project_default_tags(self):
        """ If we pass no tags, the project defaults are provided
        """
        recordings = get_recordings(self.session1.id)
        self.assertEqual([self.asset1, self.asset3], recordings)


    def test_no_assets_passing_valid_tag_list(self):
        """ Pass valid unused tag and check no assets are returned
        """
        recordings = get_recordings(self.session1.id, [self.tag3.id])
        self.assertEqual([], recordings)

    # def test_no_assets_passing_invalid_tag_list(self):
    #    """ Pass tags and check that no assets are returned
    #    """
    #    recordings = get_recordings(self.session1.id, [100])
    #    self.assertEqual([], recordings)

    def test_correct_assets_passing_tag_list(self):
        """ Pass tag lists and check for correct assets
        """
        recordings = get_recordings(self.session1.id, [self.tag1.id])
        self.assertEqual([self.asset1, self.asset3], recordings)

        recordings = get_recordings(self.session1.id, [self.tag2.id])
        self.assertEqual([self.asset2, self.asset3], recordings)

        recordings = get_recordings(self.session1.id, [self.tag1.id, self.tag2.id])
        self.assertEqual([self.asset3], recordings)

        recordings = get_recordings(self.session2.id, [self.tag1.id])
        self.assertEqual([self.asset4], recordings)

    def test_correct_assets_passing_tag_string(self):
        """ Pass tag lists and check for correct assets
        """
        recordings = get_recordings(self.session1.id, str(self.tag1.id))
        self.assertEqual([self.asset1, self.asset3], recordings)

        tag_string = str(self.tag1.id) + "," + str(self.tag2.id)
        recordings = get_recordings(self.session1.id, tag_string)
        self.assertEqual([self.asset3], recordings)

class TestFilterRecsForTags(RoundwaredTestCase):

    """ test db.filter_recs_for_tags, that it returns assets containing at 
    least one matching tag in each available tag category for tags given in
    the request.
    """

    def setUp(self):
        # gives us listen and speak ui modes, a tag1, english & spanish langs
        # and messages in english and spanish
        super(type(self), TestFilterRecsForTags).setUp(self)

        self.tagcat2, self.tagcat3, self.tagcat4 = \
            mommy.make(TagCategory, _quantity=3)
        self.tag2 = mommy.make(Tag, tag_category=self.tagcat2, value='tag2')
        self.tag3 = mommy.make(Tag, tag_category=self.tagcat3, value='tag3')
        self.project1 = mommy.make(Project, name='Project One')
        self.project2 = mommy.make(Project, name='Project Two')
        self.masterui1 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat2)
        self.masterui2 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat3)
        self.masterui3 = mommy.make(MasterUI, project=self.project2,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat1)
        self.asset1 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000)
        self.asset2 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000)
        self.asset3 = mommy.make(Asset, project=self.project2,
                                 language=self.spanish, tags=[self.tag1],
                                 audiolength=2000)
        self.asset4 = mommy.make(Asset, project=self.project2,
                                 language=self.english, tags=[self.tag1],
                                 audiolength=2000)
        self.asset5 = mommy.make(Asset, project=self.project1,
                                 language=self.english, tags=[self.tag1],
                                 audiolength=2000)
        self.asset6 = mommy.make(Asset, project=self.project1,
                                 language=self.english, tags=[self.tag1],
                                 audiolength=50)

    def test_only_assets_with_correct_tag_categories(self):
        """ 
        project 1 has assets 1,2,5,6
        project1 related to masterui1, masterui2, therefore
        tagcat2, tagcat3 are the active cats, therefore
        pass tag 1, 2 that are in categories 1 and 2
        so, assets returned must have a tag in category 2 
        so, it should return assets with tag2: = asset2
        """
        recs = filter_recs_for_tags(self.project1, [self.tag1.id, self.tag2.id],
                                    self.english)
        self.assertNotIn(self.asset1, recs)
        self.assertIn(self.asset2, recs)
        self.assertNotIn(self.asset3, recs)
        self.assertNotIn(self.asset4, recs)
        self.assertNotIn(self.asset5, recs)

    def test_assets_match_at_least_one_tag_of_all_active_tag_categories_of_passed_tags(self):
        """
        project1 has assets 1,2,5,6
        project1 related to masteruis 1,2
        masteruis 1,2 give tagcategories 2,3
        pass tag2 and tag3 that are in categories 2 and 3
        so, assets returned must have a tag in category 2 and 3
        so it should return assets with tag2 and tag3: = no assets
        asset2 matches category 2 but not 3
        """
        recs = filter_recs_for_tags(self.project1,
                                    [self.tag2.id, self.tag3.id],
                                    self.english)
        self.assertEqual([], recs)

    def test_no_assets_too_short_audiolength(self):
        recs = filter_recs_for_tags(self.project1, [self.tag1.id, self.tag2.id],
                                    self.english)
        self.assertNotIn(self.asset6, recs)

    def test_no_assets_from_wrong_projects(self):
        recs = filter_recs_for_tags(self.project1, [self.tag1.id, self.tag2.id],
                                    self.english)
        self.assertNotIn(self.asset4, recs)

    def test_only_assets_in_desired_language(self):
        recs = filter_recs_for_tags(self.project2,
                                    [self.tag1.id],
                                    self.spanish)
        self.assertIn(self.asset3, recs)  # spanish language asset
        self.assertNotIn(self.asset4, recs)  # english

    def test_no_assets_from_tags_from_inactive_masteruis(self):
        """
        project1 has assets 1,2,5,6
        project1 related to masteruis 1,2
        masterui2 now inactive
        so we only care about tagcategory 2
        pass tag 3 that's in category 3
        if masterui2 were active, we'd care about category 3
        assets returned would have had to have a tag in category 2 and 3
        but since masterui2 is inactive assets only have to have tag in cat 2
        """
        self.masterui2.active = False
        self.masterui2.save()
        recs = filter_recs_for_tags(self.project1, [self.tag3.id],
                                    self.english)
        self.assertIn(self.asset2, recs)
        self.masterui2.active = True
        self.masterui2.save()


class TestGetConfigTagJSON(RoundwaredTestCase):

    """ test various permutations of db.get_config_tag_json 
    """

    def setUp(self):
        super(type(self), TestGetConfigTagJSON).setUp(self)

        # make a masterui, a project, a ui_mode, tag category, selectionmethod
        self.english_hdr = mommy.make(LocalizedString,
                                      localized_string="Head",
                                      language=self.english)
        self.spanish_hdr = mommy.make(LocalizedString,
                                      localized_string="Cabeza",
                                      language=self.spanish)
        self.masterui = mommy.make(MasterUI, active=True,
                                   ui_mode=self.ui_mode_listen, index=1,
                                   tag_category__name='TagCatName',
                                   header_text_loc=[self.english_hdr,
                                                    self.spanish_hdr])
        self.ui_mode_one = self.masterui.ui_mode

        self.english_sess = mommy.make(Session, project=self.masterui.project,
                                       language=self.english)
        self.spanish_sess = mommy.make(Session, project=self.masterui.project,
                                       language=self.spanish)
        self.project_one = self.masterui.project
        self.ui_mapping_one = mommy.make(UIMapping, master_ui=self.masterui,
                                         active=True, tag=self.tag1,
                                         index=1, default=True)
        self.master_ui_two = mommy.make(MasterUI, name='inactivemui',
                                        ui_mode=self.ui_mode_one, active=True)
        self.project_two = self.master_ui_two.project
        self.project_three = mommy.make(Project, name='project_three')

    def _proj_one_config(self):
        # Translate the description tag like db.get_config_tag_json()
        loc_desc = ""
        temp_desc = self.ui_mapping_one.tag.loc_description.filter(language=self.english)
        if temp_desc:
            loc_desc = temp_desc[0].localized_string

        return {'listen': [
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
                 'description': self.ui_mapping_one.tag.description,
                 'loc_description': loc_desc,
                 'shortcode': self.ui_mapping_one.tag.value,
                 'relationships': [],
                 'value': 'One'
             }]},
        ]}

    def test_get_uimapping_info_for_project(self):
        """ Test proper UIMapping data returned based on project passed """
        config = get_config_tag_json(self.project_one, self.english_sess)
        expected = self._proj_one_config()
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
                          config['listen']])

    def test_session_project_overrides_passed_project(self):
        """ The project associated with a passed session should be used 
            even if a project is explicitly passed. (really?)
        """
        pass

    def test_only_active_masteruis_returned(self):
        """ Confirm that only active MasterUIs are returned in 
            config tag 'JSON' (dictionary)
        """
        self.master_ui_two.active = False
        self.master_ui_two.save()
        config = get_config_tag_json(self.project_two)
        self.assertEquals({}, config)
        self.master_ui_two.active = True
        self.master_ui_two.save()

    def test_get_right_masterui_without_passed_project(self):
        """ Don't pass a project, just use the project for the session.
            Do we still get the right MasterUI?
        """
        config = get_config_tag_json(None, self.english_sess)
        expected = self._proj_one_config()
        self.assertEquals(expected, config)

    def test_get_correct_localized_header_text(self):
        """ Test that we get correct localized header text for session, or if 
            none passed, header text in English.
        """
        config = get_config_tag_json(None, self.spanish_sess)
        self.assertEquals('Cabeza',
                          config['listen'][0]['header_text'])

    def test_tag_values_correctly_localized(self):
        """ Test that we get correct localized text for tag values
            based on session language, or if none passed, in English.
        """
        config = get_config_tag_json(None, self.spanish_sess)
        self.assertEquals('Uno',
                          config['listen'][0]['options'][0]['value'])


class TestListeningHistoryDB(RoundwaredTestCase):

    def setUp(self):
        super(type(self), TestListeningHistoryDB).setUp(self)

        self.project1 = mommy.make(Project)
        self.asset1 = mommy.make(Asset, project=self.project1)
        self.asset2 = mommy.make(Asset, project=self.project1)
        self.history1 = mommy.make(ListeningHistoryItem, asset=self.asset1,
                                   session=self.default_session,
                                   starttime=datetime.datetime.now())
        self.history2 = mommy.make(ListeningHistoryItem, asset=self.asset2,
                                   session=self.default_session,
                                   starttime=datetime.datetime.now())

    def test_get_current_streaming_asset(self):
        self.assertEquals(self.history2, get_current_streaming_asset(
                          self.default_session.id))

    def test_cleanup_history_for_session(self):
        cleanup_history_for_session(self.default_session)
        self.assertEquals(None, get_current_streaming_asset(
                          self.default_session.id))
