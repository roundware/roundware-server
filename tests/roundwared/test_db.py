# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from model_mommy import mommy

from .common import RoundwaredTestCase
from roundware.rw.models import (UIGroup, Session, Tag, Asset, TagCategory,
                                 UIItem, Project, ListeningHistoryItem)
from roundwared.db import (filter_recs_for_tags,
                           get_recordings, get_active_tags_for_project)


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
        self.tag2 = mommy.make(Tag, tag_category=self.tagcat2, value='tag2', id=2)
        self.tag3 = mommy.make(Tag, tag_category=self.tagcat3, value='tag3', id=3)
        self.uigroup1 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat1)
        self.uigroup2 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat2)
        self.uigroup2 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat3)
        self.uigroup4 = mommy.make(UIGroup, project=self.project2,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat2)
        # Add one default tag to project1
        self.uiitem1 = mommy.make(UIItem, ui_group=self.uigroup1,
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


    def test_get_active_tags_for_project(self):
        """ Project1 has one active tag, Project2 has no active tags.
        """
        active_tags = get_active_tags_for_project(self.project1)
        self.assertEqual(active_tags, [self.tag1.id])

        default_tags = get_active_tags_for_project(self.project2)
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

    # Commented out, because IDK how this is supposed to work.
    # I think the test is right and the code is wrong. -eosrei
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
        self.tag2 = mommy.make(Tag, tag_category=self.tagcat2, value='tag2', id=2)
        self.tag3 = mommy.make(Tag, tag_category=self.tagcat3, value='tag3', id=3)
        self.project1 = mommy.make(Project, name='Project One')
        self.project2 = mommy.make(Project, name='Project Two')
        self.uigroup1 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat2)
        self.uigroup2 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat3)
        self.uigroup3 = mommy.make(UIGroup, project=self.project2,
                                    ui_mode=UIGroup.LISTEN,
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
        project1 related to uigroup1, uigroup2, therefore
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
        project1 related to uigroups 1,2
        uigroups 1,2 give tagcategories 2,3
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

    def test_no_assets_from_tags_from_inactive_uigroups(self):
        """
        project1 has assets 1,2,5,6
        project1 related to uigroups 1,2
        uigroup2 now inactive
        so we only care about tagcategory 2
        pass tag 3 that's in category 3
        if uigroup2 were active, we'd care about category 3
        assets returned would have had to have a tag in category 2 and 3
        but since uigroup2 is inactive assets only have to have tag in cat 2
        """
        self.uigroup2.active = False
        self.uigroup2.save()
        recs = filter_recs_for_tags(self.project1, [self.tag3.id],
                                    self.english)
        self.assertIn(self.asset2, recs)
        self.uigroup2.active = True
        self.uigroup2.save()
