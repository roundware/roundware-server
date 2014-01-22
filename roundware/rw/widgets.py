from django.forms import Media
from django.contrib.admin.widgets import (RelatedFieldWidgetWrapper,
                                          FilteredSelectMultiple)
from django.contrib.admin.templatetags.admin_static import static
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from sortedm2m.forms import SortedCheckboxSelectMultiple


STATIC_URL = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)


# taken nearly wholesale from 
# http://dashdrum.com/blog/2012/12/more-relatedfieldwidgetwrapper-the-popup/

class NonAdminRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    """
        Based on RelatedFieldWidgetWrapper, this does the same thing
        outside of the admin interface

        the parameters for a relation and the admin site are replaced
        by a url for the add operation
    """

    def __init__(self, widget, add_url, permission=True):
        self.is_hidden = widget.is_hidden
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.choices = widget.choices
        self.widget = widget
        self.add_url = add_url
        self.permission = permission

    def render(self, name, value, *args, **kwargs):
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        if self.permission:
            output.append(u'<br/><a href="%s" class="add-another" id="add_id_%s" '
                          'onclick="return showAddAnotherPopup(this);"> ' % 
                          (self.add_url, name))
            output.append(u'<img src="%simg/icon_addlink.gif" width="10"'
                          ' height="10" alt="%s"/>&nbsp;&nbsp;%s</a>' % 
            (settings.ADMIN_MEDIA_PREFIX, _('Add Another'), _('Add Another')))
        return mark_safe(u''.join(output))


class SetupTagUIFilteredSelectMultiple(FilteredSelectMultiple):

    @property
    def media(self):
        """ add jquery.init.js to get 'django' JQuery namespace 
            and setup_tag_ui.js which should be in the form class so we 
            define $.  ugh.
        """
        js = ["admin/js/core.js", "admin/js/jquery.init.js", 
              "/static/rw/js/setup_tag_ui.js", 
              "admin/js/SelectBox.js", "admin/js/SelectFilter2.js"]
        return Media(js=[static(path) for path in js])

    def render(self, name, value, attrs=None, choices=()):
        """ we need to fire SelectFilter.init whenever the html is re-written
            after AJAX call from selection form
        """    
        if attrs is None:
            attrs = {}
        attrs['class'] = 'selectfilter'
        if self.is_stacked:
            attrs['class'] += 'stacked'
        output = [super(FilteredSelectMultiple, self).render(
            name, value, attrs, choices)]
        output.append('<script type="text/javascript">')
        output.append('function rewriteFilteredSelect(){')
        output.append('SelectFilter.init("id_%s", "%s", %s, "%s"); }\n' % (
            name, self.verbose_name.replace('"', '\\"'),
            int(self.is_stacked), static('admin/'))
        )
        output.append('addEvent(window, "load", function(e) {')
        output.append('rewriteFilteredSelect()});</script>\n')

        return mark_safe(''.join(output))


class SetupTagUISortedCheckboxSelectMultiple(SortedCheckboxSelectMultiple):

    class Media:
        js = (
            "admin/js/core.js", 
            "admin/js/jquery.init.js", 
            "/static/rw/js/setup_tag_ui.js", 
            "/static/rw/js/sortedmulticheckbox_widget.js",
            "/static/sortedm2m/jquery-ui.js",
        )
        css = {'screen': (
            STATIC_URL + 'sortedm2m/widget.css',
        )}

