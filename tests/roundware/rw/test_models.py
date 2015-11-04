# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals

from model_mommy import mommy

from roundware.rw import models
from roundware.settings import DEFAULT_SESSION_ID

from .common import use_locmemcache, RWTestCase

class TestMasterUI(RWTestCase):

    """ exercise MasterUI model class """

    def setUp(self):
        super(type(self), TestMasterUI).setUp(self)

        # make masterui, makes our tagcategory, uimode, project,
        # selectionmethod
        self.masterui = mommy.make('rw.MasterUI')
        self.other_uimode = models.MasterUI.SPEAK
        self.project = self.masterui.project

    @use_locmemcache(models, 'cache')
    def test_tag_category_cache_invalidation_post_save(self):
        """ test that cached value for tag categories for the MasterUI's mode
        is invalidated after MasterUI saved.
        """
        ui_mode = self.masterui.ui_mode
        get_orig_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode)

        # is original tag_cat of masterui returned by Project's method
        self.assertIn(self.masterui.tag_category, get_orig_tag_cats)

        # change the ui mode of our masterui
        self.masterui.ui_mode = self.other_uimode

        # should still get old tag categories... cached
        get_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode)
        self.assertIn(self.masterui.tag_category, get_tag_cats)

        # save the masterui, now should not get old tag categories...
        # cached copy invalidated
        self.masterui.save()
        get_tag_cats = self.project.get_tag_cats_by_ui_mode(ui_mode)
        self.assertNotIn(self.masterui.tag_category, get_tag_cats)
        
    # Karl
    def test_get_header_text_loc(self):
        self.assertEquals('', self.masterui.get_header_text_loc())
    
    def test_toTagDictionary(self):
        output = ""
        sequence = ({u'code': u'fJyTlBrUQSTZgrVXcBLfcvgiMeGlGcFARIcLfiLtpBmtoVUDQh', u'name': u'ConfAnyCfUvcRGOAoFoyMKwRwaWhDUZceBehQjYHYosywLGuAr', u'select': u'single', u'order': -8309})
        return (output.join(sequence), self.masterui.toTagDictionary())
    
    # Karl
    def test___unicode__(self):
        self.assertEquals("1:" + self.project.name + ":" + self.masterui.get_ui_mode_display() + ":" + self.masterui.name, self.masterui.__unicode__())
        

class TestProject(RWTestCase):

    def setUp(self):
        super(type(self), TestProject).setUp(self)
        self.project = mommy.make('rw.Project')
        self.ui_mode = models.MasterUI.LISTEN

    def test_no_tag_cats_returned_new_project(self):
        """ test no tag_categories returned for a new project with no masterui
        """
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode)
        self.assertTrue(len(cats) == 0)

    def test_correct_tag_cats_returned(self):
        """ test that we get correct tagcategories for our project once
            we add a MasterUI.
        """
        masterui = mommy.make('rw.MasterUI', project=self.project,
                              ui_mode=self.ui_mode)
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode)
        self.assertIn(masterui.tag_category, cats)

    def test_no_tag_cats_returned_wrong_uimode(self):
        """ test no tag_categories returned if we specify a uimode that 
            is not connected to project via a MasterUI
        """
        other_master_ui = mommy.make('rw.MasterUI', project=self.project,
                                     ui_mode=models.MasterUI.SPEAK)
        cats = self.project.get_tag_cats_by_ui_mode(self.ui_mode)
        self.assertNotIn(other_master_ui.tag_category, cats)
        
class TestAsset(RWTestCase):

    def setUp(self):
        super(type(self), TestAsset).setUp(self)

        self.session1 = mommy.make('rw.Session', id=DEFAULT_SESSION_ID)
        self.session2 = mommy.make('rw.Session')
        self.project = mommy.make('rw.Project')
        self.asset1 = mommy.make('rw.Asset')
        self.asset2 = mommy.make('rw.Asset')
        self.vote1 = mommy.make('rw.Vote', session=self.session1,
                                asset=self.asset1, type="like")
        self.vote2 = mommy.make('rw.Vote', session=self.session2,
                                asset=self.asset1, type="like")
        self.vote3 = mommy.make('rw.Vote', session=self.session1,
                                asset=self.asset2, type="like")
        self.vote4 = mommy.make('rw.Vote', session=self.session1,
                                asset=self.asset1, type="flag")

    
    # Karl
    def test_media_display(self):
        self.assertEquals(self.asset1.audio_player(), self.asset1.media_display())


    # Karl
    def test_audio_player(self):
        self.assertEquals('<div data-filename="None" class="media-display audio-file"></div>', self.asset1.audio_player())


    # Karl
    def test_image_display(self):
        self.assertEquals('<div data-filename="None" class="media-display image-file"><a href="/rwmedia/None" target="imagepop"><img src="/rwmedia/None" alt="" title="click for full image"/></a></div>', self.asset1.image_display())


    # Karl
    def test_text_display(self):
        self.assertEquals('<div data-filename="None" class="media-display text-file"\n'
                          '                   >mock file\n'
                          ' </div>', self.asset1.text_display())


    # Karl
    def test_location_map(self):
        self.assertEquals('<input type="text" value="" id="searchbox" style=" width:700px;height:30px; font-size:15px;">\n        <div id="map_instructions">To change or select location, type an address above and select from the available options;\n        then move pin to exact location of asset.</div>\n        <div class="GMap" id="map" style="width:800px; height: 600px; margin-top: 10px;"></div>', self.asset1.location_map())


    # Karl
    def test_norm_audiolength(self):
        self.assertEquals(None, self.asset1.norm_audiolength())
        self.assertEquals(self.asset1.audiolength, self.asset1.norm_audiolength())
        self.assertEquals(None, self.asset2.norm_audiolength())
        self.assertEquals(self.asset2.audiolength, self.asset2.norm_audiolength())


    # Karl
    def test_media_link_url(self):
        self.assertEquals('<a href="/rwmedia/None" target="_new">None</a>', self.asset1.media_link_url())
    
    # Karl
    def test_get_tags(self):
        self.assertEquals("", self.asset1.get_tags())

    def test_get_likes(self):
        self.assertEquals(2, self.asset1.get_likes())
        self.assertEquals(1, self.asset2.get_likes())

    def test_get_flags(self):
        self.assertEquals(1, self.asset1.get_flags())
        
    # Karl
    def test_get_votes(self):
        self.assertEquals("flag : 0, like : 0", self.asset1.get_votes())

        
class TestLocalizedString(RWTestCase):
    def setUp(self):
        super(type(self), TestLocalizedString).setUp(self)
        self.localized_string = mommy.make('rw.LocalizedString')
        
    def test___unicode__(self):
        self.assertEquals('1: Language Code: ' + str(self.localized_string.language.language_code) + ', String: ' + str(self.localized_string.localized_string), self.localized_string.__unicode__())
        
# Karl
class TestSession(RWTestCase):
    # Karl
    def setUp(self):
        super(type(self), TestSession).setUp(self)
        self.project = mommy.make('rw.Session')

    # Karl
    def test___unicode__(self):
        self.assertEquals('1', self.project.__unicode__())

class TestTag(RWTestCase):
    def setUp(self):
        super(type(self), TestTag).setUp(self)
        self.project = mommy.make('rw.Tag')
    
    def test_get_loc(self):
        self.assertEquals('', self.project.get_loc())
    
    def test___unicode__(self):
        self.assertEquals(self.project.tag_category.name + " : " + self.project.value, self.project.__unicode__())

class TestUIMapping(RWTestCase):
    
    def setUp(self):
        super(type(self), TestUIMapping).setUp(self)
        self.master_ui = mommy.make('rw.MasterUI')
        self.project = mommy.make('rw.UIMapping')

    def test___unicode__(self):
        self.assertEquals("1:" + self.project.master_ui.name + ":" + self.project.tag.tag_category.name, self.project.__unicode__())

class TestAudiotrack(RWTestCase):
    
    def setUp(self):
        super(type(self), TestAudiotrack).setUp(self)
        self.project = mommy.make('rw.Audiotrack')
    
    def test_norm_minduration(self):
        if (self.project.norm_minduration() == '0.00 s'):
            self.assertEquals('0.00 s', self.project.norm_minduration())
        elif (self.project.norm_minduration() == '-0.00 s'):
            self.assertEquals('-0.00 s', self.project.norm_minduration())
    
    def test_norm_maxduration(self):
        if (self.project.norm_maxduration() == '0.00 s'):
            self.assertEquals('0.00 s', self.project.norm_maxduration())
        elif (self.project.norm_maxduration() == '-0.00 s'):
            self.assertEquals('-0.00 s', self.project.norm_maxduration())

    def test_norm_mindeadair(self):
        if (self.project.norm_mindeadair() == '0.00 s'):
            self.assertEquals('0.00 s', self.project.norm_mindeadair())
        elif (self.project.norm_mindeadair() == '-0.00 s'):
            self.assertEquals('-0.00 s', self.project.norm_mindeadair())

    def test_norm_maxdeadair(self):
        if (self.project.norm_maxdeadair() == '0.00 s'):
            self.assertEquals('0.00 s', self.project.norm_maxdeadair())
        elif (self.project.norm_maxdeadair() == '0.00 s'):
            self.assertEquals('-0.00 s', self.project.norm_maxdeadair())

    def test___unicode__(self):
        self.assertEquals('Track 1', self.project.__unicode__())
        
class TestEnvelope(RWTestCase):
    def setUp(self):
        super(type(self), TestEnvelope).setUp(self)
        self.project = mommy.make('rw.Envelope')


        
class TestSpeaker(RWTestCase):
    def setUp(self):
        super(type(self), TestSpeaker).setUp(self)
        self.project = mommy.make('rw.Speaker')
    
    def test___unicode__(self):
        self.assertEquals('1: ' + str(self.project.latitude) + "/" + str(self.project.longitude)  + " : " + str(self.project.uri), self.project.__unicode__())
    
    def test_location_map(self):
        self.assertEquals('<input type="text" value="" id="searchbox" style=" width:700px;height:30px; font-size:15px;">\n        <div id="map_instructions">To change or select location, type an address above and select from the available options;\n        then move pin to exact location of asset.</div>\n        <div class="GMap" id="map" style="width:800px; height: 600px; margin-top: 10px;"></div>', self.project.location_map())


class TestListeningHistoryItem(RWTestCase):
    def setUp(self):
        super(type(self), TestListeningHistoryItem).setUp(self)
        self.project = mommy.make('rw.ListeningHistoryItem')
    
    def test_norm_duration(self):
        self.assertEquals(None, self.project.norm_duration())
    
    def test_duration_in_seconds(self):
        self.assertEquals(None, self.project.duration_in_seconds())

    def test__unicode__(self):
        self.assertEquals('1: Session id: 1: Asset id: 1 duration: None', self.project.__unicode__())