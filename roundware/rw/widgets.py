#***********************************************************************************#

# ROUNDWARE
# a contributory, location-aware media platform

# Copyright (C) 2008-2014 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry, Ben McAllister, Jule Slootbeek and Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


from itertools import chain

from django.forms import Media, Widget, CheckboxInput
from django.contrib.admin.widgets import (RelatedFieldWidgetWrapper,
                                          FilteredSelectMultiple)
from django.contrib.admin.templatetags.admin_static import static
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

# import floppyforms as forms
from sortedm2m.forms import SortedCheckboxSelectMultiple

from roundware.rw.models import Tag


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


class DummyWidgetWrapper(Widget):
    """ Return a widget.  For some reason, having to use this to get around
        using the CheckboxFieldRenderer from django.forms.widgets for our
        SetupTagUISortedCheckboxSelectMultiple
    """

    def __init__(self, widget):
        self.widget = widget
        self.is_hidden = widget.is_hidden
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.choices = widget.choices

    def render(self, name, value, *args, **kwargs):
        self.widget.choices = self.choices
        return self.widget.render(name, value, *args, **kwargs)

    @property
    def media(self):
        return self.widget.media

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        self.attrs = self.widget.build_attrs(extra_attrs=None, **kwargs)
        return self.attrs

    def value_from_datadict(self, data, files, name):
        return self.widget.value_from_datadict(data, files, name)

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)


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

        # import pdb; pdb.set_trace()

        output.append('function setupTagOrderSelectChange() {\n')
        output.append('$("select[name=\'master_ui_edit-ui_mappings_tags\']").change(function(){\n')
        output.append('$(\'#uimap_tag_order_field\').load(\'./update_tag_ui_order #tag_order_inner\', '
                      '{tags: $.map($(this).find(\'option\'), function(option) {return option.value;}), '
                      ' mui:$(\'#id_master_ui_select-masterui\').val() }, rewriteSortedMultiCheckbox)\n')
        output.append('});\n')
        output.append('};\n')

        output.append('function rewriteFilteredSelect(){\n')
        output.append('SelectFilter.init("id_%s", "%s", %s, "%s"); \n' % (
            name, self.verbose_name.replace('"', '\\"'),
            int(self.is_stacked), static('admin/'))
        )
        # force Webkit redraw
        output.append('$(\'#div_id_%s .selector\').hide().show(0);\n' % name)
        output.append('setupTagOrderSelectChange();};\n')
        output.append('addEvent(window, "load", function(e) {\n')
        output.append('rewriteFilteredSelect()});</script>\n')

        return mark_safe(''.join(output))


class SetupTagUISortedCheckboxSelectMultiple(SortedCheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=(), new_maps=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)

        # Normalize to strings
        str_values = [force_text(v) for v in value]

        vals = []
        last_uimap = 0

        for i, (option_value, option_label) in enumerate(chain(self.choices,
                                                               choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = ' for="%s"' % conditional_escape(final_attrs['id'])
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs,
                check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))
            item = {'label_for': label_for, 'rendered_cb': rendered_cb,
                    'option_label': option_label, 'option_value': option_value}
            vals.append(item)
            last_uimap += 1

        for i, newmap in enumerate(new_maps):

            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'],
                                   i+last_uimap))
                label_for = ' for="%s"' % conditional_escape(final_attrs['id'])
            else:
                label_for = ''
            cb = CheckboxInput(final_attrs,
                 check_test = lambda l: False)
            option_value = 't'+str(newmap.id)
            rendered_cb = cb.render(name, option_value)
            option_label = newmap.__unicode__()
            option_label = conditional_escape(force_text(option_label))
            item = {'label_for': label_for, 'rendered_cb': rendered_cb,
                    'option_label': option_label, 'option_value': option_value}
            vals.append(item)

        html = render_to_string(
            'sortedm2m/sorted_checkbox_select_multiple_widget.html',
            {'vals': vals, })
        return mark_safe(html)


    class Media:
        js = (
            # "admin/js/core.js",
            # "admin/js/jquery.init.js",
            # "/static/rw/js/setup_tag_ui.js",
            "/static/rw/js/sortedmulticheckbox_widget.js",
            "/static/sortedm2m/jquery-ui.js",
        )
        css = {'screen': (
            STATIC_URL + 'sortedm2m/widget.css',
        )}


