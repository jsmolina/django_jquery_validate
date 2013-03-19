
from django.template import loader, Node, Variable
from django.utils.encoding import smart_str, smart_unicode
from django.template.defaulttags import url
from django.template import VariableDoesNotExist


from django import template

from simplejson import dumps, loads


register = template.Library()


@register.simple_tag
def validate(form, form_id):
    """
    Validates form
    :param form:
    :param form_id:
    :return:
    """
    validate_str = ""
    validate_dict = {'rules': {}, 'messages': {}, "success": ""}

    for field in form:
        validate_dict['rules'][field.name] = loads(field.field.widget.attrs["cls"])
        del field.field.widget.attrs["cls"]

    for field in form:
        validate_dict['messages'][field.name] = {}

        for key in field.field.widget.attrs['msg']:
            validate_dict['messages'][field.name][key] = field.field.widget.attrs['msg'][key]

        del field.field.widget.attrs['msg']

    validate_str += "<script type='text/javascript' src='/static/js/jquery.validate.min.js'></script>"
    validate_str += "<script type='text/javascript'>"
    validate_str += "$(document).ready(function() {"
    validate_dict['success'] = "##function(label) { "+ \
                               "    label.removeClass('error'); label.parent().removeClass('status-error'); label.remove();"+ \
                               "}##"


    validate_dict['showErrors'] = "## function(errorMap, errorList) {" +\
        "this.defaultShowErrors();"+ \
                                  "$('label.error').parent().addClass('status-error')"+ \
                                  "}##"
    validate_str += "   $('#%s').validate(%s);" % (form_id, dumps(validate_dict))

    validate_str += "});"
    validate_str += '</script>'
    validate_str = validate_str.replace("\"##", "")
    validate_str = validate_str.replace("##\"", "")

    return validate_str
