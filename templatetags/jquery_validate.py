
from django.template import loader, Node, Variable
from django.utils.encoding import smart_str, smart_unicode
from django.template.defaulttags import url
from django.template import VariableDoesNotExist


from django import template

from simplejson import dumps, loads


register = template.Library()

@register.simple_tag
def validate_server(form, field):
    error_str = ""

    if field in form.errors:
        error_str = """<label for="id_%s" class="error" style="display: inline;">
            <div class="error-wrapper "><p class="error"> %s </p></div>
            </label>""" % (field, form.errors[field][0])
    return error_str

@register.simple_tag
def validate(form, form_id):
    """
    Validates form
    :param form:
    :param form_id:
    :return:
    """
    validate_str = ""
    validate_dict = {'onkeyup': False,  'rules': {}, 'messages': {}, "success": "", 'ignore': '.ignore'}

    for field in form:
        validate_dict['rules'][field.name] = loads(field.field.widget.attrs["cls"])
        del field.field.widget.attrs["cls"]
        if 'remote' in field.field.widget.attrs:
            del field.field.widget.attrs["remote"]

        if 'custom' in field.field.widget.attrs:
            del field.field.widget.attrs["custom"]

    for field in form:
        validate_dict['messages'][field.name] = {}

        for key in field.field.widget.attrs['msg']:
            validate_dict['messages'][field.name][key] = field.field.widget.attrs['msg'][key]

        del field.field.widget.attrs['msg']


    validate_str += "<script type='text/javascript' src='/static/js/jquery.validate.min.js'></script>"
    validate_str += "<script type='text/javascript' src='/static/js/additional-methods.min.js'></script>"
    validate_str += "<script type='text/javascript'>"
    validate_str += "$(document).ready(function() {"
    validate_dict['success'] = "##function(label) { "+ \
                               "    label.removeClass('error'); label.parent().removeClass('status-error'); label.remove();"+ \
                               "}##"


    validate_dict['showErrors'] = "## function(errorMap, errorList) {" +\
        "this.defaultShowErrors();"+ \
                                  "$('label.error').parent().addClass('status-error')"+ \
                                  "}##"
    validate_str += "   $('#%s').validate(%s);" % (form_id, dumps(validate_dict, sort_keys=True))

    validate_str += "});"
    validate_str += '</script>'
    validate_str = validate_str.replace("\"##", "")
    validate_str = validate_str.replace("##\"", "")

    return validate_str
