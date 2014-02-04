import string
import os
import logging
import json
import traceback

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.forms.models import save_instance

from guardian.core import ObjectPermissionChecker
from guardian.mixins import PermissionRequiredMixin
from braces.views import (LoginRequiredMixin, FormValidMessageMixin, 
                          AjaxResponseMixin)
from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView
from extra_views.multi import MultiFormView, FormProvider

from roundware.rw.chart_functions import assets_created_per_day
from roundware.rw.chart_functions import sessions_created_per_day
from roundware.rw.chart_functions import assets_by_question
from roundware.rw.chart_functions import assets_by_section
from roundware.rw.models import Tag, MasterUI, UIMapping, Project
from roundware.rw.forms import (TagCreateForm, BatchTagFormset, 
                                # MasterUIForSetupTagUICreateForm,
                                MasterUIForSetupTagUIEditForm,
                                MasterUIForSetupTagUISelectForm)
from roundwared import settings
from roundwared import roundexception
from roundwared import server



def main(request):
    return HttpResponse(json.dumps(catch_errors(request), sort_keys=True, indent=4, ensure_ascii=False), mimetype='application/json')


def catch_errors(request):
    try:
        config_file = "rw"
        if request.GET.has_key('config'):
            config_file = request.GET['config']
        settings.initialize_config(os.path.join('/etc/roundware/', config_file))

        logging.basicConfig(
            filename=settings.config["log_file"],
            filemode="a",
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s',
            )

        if request.GET.has_key('operation'):
            function = operation_to_function(request.GET['operation'])
        elif request.POST.has_key('operation'):
            function = operation_to_function(request.POST['operation'])
        return function(request)
    except roundexception.RoundException as e:
        logging.error(str(e) + traceback.format_exc())
        return {"error_message": str(e)}
    except:
        logging.error(
            "An uncaught exception was raised. See traceback for details." + \
            traceback.format_exc())
        return {
            "error_message": "An uncaught exception was raised. See traceback for details.",
            "traceback": traceback.format_exc(),
        }


def operation_to_function(operation):
    if not operation:
        raise roundexception.RoundException("Operation is required")
    operations = {
        "request_stream": server.request_stream,
        "heartbeat": server.heartbeat,
        "current_version": server.current_version,
        "log_event": server.log_event,
        "create_envelope": server.create_envelope,
        "add_asset_to_envelope": server.add_asset_to_envelope,
        "get_config": server.get_config,
        "get_tags": server.get_tags_for_project,
        "modify_stream": server.modify_stream,
        "get_current_streaming_asset": server.get_current_streaming_asset,
        "get_asset_info": server.get_asset_info,
        "get_available_assets": server.get_available_assets,
        "play_asset_in_stream": server.play_asset_in_stream,
        "vote_asset": server.vote_asset,
        "skip_ahead": server.skip_ahead,
    }
    key = string.lower(operation)
    if operations.has_key(key):
        return operations[key]
    else:
        raise roundexception.RoundException("Invalid operation, " + operation)


from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required


@login_required
def chart_views(request):

    asset_created_per_day_chart = assets_created_per_day()
#    return render_to_response("chart_template.html", {'assetchart': asset_created_per_day_chart})

    session_created_per_day_chart = sessions_created_per_day()
    assets_by_question_chart = assets_by_question()
    assets_by_section_chart = assets_by_section()
#    return render_to_response("chart_template.html", {'sessionchart': session_created_per_day_chart, 'assetchart': asset_created_per_day_chart})
    return render_to_response("chart_template.html", {'charts': [session_created_per_day_chart, asset_created_per_day_chart, assets_by_question_chart, assets_by_section_chart]})


class MultiCreateTagsView(LoginRequiredMixin, FormValidMessageMixin, MultiFormView):
    success_url = '/admin/rw/tag'
    template_name = 'rw/tags_add_to_category_form.html'
    form_valid_message = 'Tags created!'
    forms = {'category': MultiFormView.modelform(Tag, TagCreateForm, 
                         **{'fields': ('tag_category',),
                            'exclude': ('value','description','data',
                                        'loc_msg')}
                         ),
             'tag_formset': MultiFormView.modelformset(Tag,
                            **{'extra': 2, 'form': TagCreateForm,
                               'exclude': ['tag_category'],
                               'fields': ['value', 'description', 'data', 'loc_msg'],
                               'formset': BatchTagFormset}
                            )
            }

    def get_category_instance(self):
        return Tag()

    def get_tag_formset_queryset(self):
        return Tag.objects.none()

    def valid_all(self, valid_forms):
        """ handle case all forms valid 
        """
        category= valid_forms['category']
        formset= valid_forms['tag_formset']
        for form in formset.forms:
            tag = form.save(commit=False)  # doesn't save m2m yet
            tag.tag_category = category.cleaned_data['tag_category']
            tag.save()
            form.save_m2m()

    def invalid_all(self, invalid_forms):
        """ handle case all forms invalid
        """
        self.forms_invalid(invalid_forms)


class UIMappingsInline(InlineFormSet):
    model = UIMapping
    fk_name = 'master_ui'


class SetupTagUIMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """ make sure User can modify this MasterUI based on Project,
        and is logged in.
    """    
    permission_required = 'rw.access_project'
    return_403 = True

    def get_object(self):
        """ return Project for this MasterUI  as the object to check against
        """
        try:
            return get_object_or_404(Project, masterui=self.kwargs['pk'])
        except KeyError:
            return None


class MasterUIMappingsOrganizationView(SetupTagUIMixin, AjaxResponseMixin, 
                                       MultiFormView):
    success_url = '.'
    template_name = 'setup_tag_ui_form.html'
    forms = {
        'master_ui_select': FormProvider(
        MasterUIForSetupTagUISelectForm,
        context_suffix='form', 
        init_args={'user': 'get_%s_user'}),

        'master_ui_edit': MultiFormView.modelform(
                          MasterUI, 
                          MasterUIForSetupTagUIEditForm),           
    }

    def get_master_ui_select_user(self):
        return self.request.user

    def get_master_ui_edit_instance(self):
        """ for calling with a primary key in the url. This is called magically
            by MultiFormView to get the instance for master_ui_edit form
        """
        if self.kwargs.get('pk'):            
            return MasterUI.objects.filter(pk=self.kwargs['pk'])[0]
        else:
            return MasterUI()

    def post(self, request, *args, **kwargs):
        """ create or update MasterUI instance
        """
        return super(MasterUIMappingsOrganizationView, self).post(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        """ handle post made from selecting MasterUI in 'master_ui_select'
            form. AJAX posts will only result from modelchoicefield select
            for MasterUI changing.
        """
        edit_form_template = 'rw/setup_tags_ui_edit_form.html'
        response_dic = {}

        # if modelchoicefield not empty
        if request.POST.get("master_ui_select-masterui"):
            id_to_update = request.POST["master_ui_select-masterui"]
            mui=MasterUI.objects.get(pk=id_to_update)
            edit_form = MasterUIForSetupTagUIEditForm(instance=mui)
            response_dic['mui_update_id'] = mui.id

        else:
            edit_form = MasterUIForSetupTagUIEditForm()

        response_dic['master_ui_edit_form'] = edit_form

        return HttpResponse(render_to_string(edit_form_template, 
                                             response_dic, 
                                             RequestContext(request)))

    def update_ui_mappings(self, uimaps, formtags, defaults, indexes, mui):
        uimaptags = []
        default_tags = [df.tag for df in defaults]
        for uimap in uimaps:
            uimaptags.append(uimap.tag)
            if uimap.tag not in formtags:
                uimap.delete()
        for tag in formtags:  
            index = indexes.index(tag.pk) + 1
            default = tag in default_tags
            if tag not in uimaptags:
                uimap = UIMapping(tag=tag, master_ui=mui, active=True, 
                                  index=index, default=default)
                uimap.save()
            else:
                uimap = [uim for uim in uimaps if uim.tag == tag][0]
                uimap.index = index
                uimap.default = default
                uimap.save()

    def valid_all(self, valid_forms):
        """ handle case all forms valid 
        """

        select = valid_forms['master_ui_select']  # don't save anything
        select  # pyflakes
        form = valid_forms['master_ui_edit']
        mui_id = form.cleaned_data.get('id')
        formtags = form.cleaned_data['ui_mappings_tags']
        defaults = form.cleaned_data['ui_mappings_tag_order']
        indexes = form.cleaned_data['ui_mappings_tags_indexes'].split(',')
        indexes = [UIMapping.objects.select_related('tag').filter(
                   pk=uimap)[0].tag.pk for uimap in indexes]
        if mui_id:
            mui = MasterUI.objects.filter(pk=mui_id)[0]
            uimaps = UIMapping.objects.select_related(
                     'tag').filter(master_ui=mui)
            # instance isn't constructed yet with data from form so we can't
            # use form.save() but have to do the following with construct=True            
            save_instance(form, mui, form._meta.fields, 'form changed', True, 
                          form._meta.exclude, True)
            self.update_ui_mappings(uimaps, formtags, defaults, indexes, mui)
            
        else:
            mui = form.save()
            self.update_ui_mappings([], formtags, defaults, indexes, mui)

    def invalid_all(self, invalid_forms):
        """ handle case all forms invalid
        """
        self.forms_invalid(invalid_forms)



