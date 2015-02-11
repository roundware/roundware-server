from __future__ import unicode_literals
from roundware.rw import models
from roundware.lib.exception import RoundException
import logging

logger = logging.getLogger(__name__)


def t(msg, field, language):
    """
    Locates the translation for the msg in the field object for the provided
    session language.
    """
    # TODO: Replace with standard Django internationalization.
    try:
        msg = field.filter(language=language)[0].localized_string
    except:
        pass
    return msg


# @profile(stats=True)
def get_config_tags(p=None, s=None):
    if s is None and p is None:
        raise RoundException("Must pass either a project or a session")
    language = models.Language.objects.filter(language_code='en')[0]
    if s is not None:
        p = s.project
        language = s.language

    m = models.MasterUI.objects.filter(project=p)
    modes = {}

    for masterui in m:
        if masterui.active:
            mappings = models.UIMapping.objects.filter(
                master_ui=masterui, active=True)
            header = t("", masterui.header_text_loc, language)

            masterD = {'name': masterui.name,
                       'header_text': header,
                       'code': masterui.tag_category.name,
                       'select': masterui.get_select_display(),
                       'order': masterui.index
                       }
            masterOptionsList = []

            default = []
            for mapping in mappings:
                loc_desc = t("", mapping.tag.loc_description, language)
                if mapping.default:
                    default.append(mapping.tag.id)
                # masterOptionsList.append(mapping.toTagDictionary())
                # def toTagDictionary(self):
                    # return
                    # {'tag_id':self.tag.id,'order':self.index,'value':self.tag.value}

                masterOptionsList.append({'tag_id': mapping.tag.id, 'order': mapping.index, 'data': mapping.tag.data,
                                          'relationships': mapping.tag.get_relationships(),
                                          'description': mapping.tag.description, 'shortcode': mapping.tag.value,
                                          'loc_description': loc_desc,
                                          'value': t("", mapping.tag.loc_msg, language)})
            masterD["options"] = masterOptionsList
            masterD["defaults"] = default
            if masterui.ui_mode not in modes:
                modes[masterui.ui_mode] = [masterD, ]
            else:
                modes[masterui.ui_mode].append(masterD)

    return modes
