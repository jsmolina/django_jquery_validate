from django import template
from simplejson import dumps, loads
from django.utils.translation import ugettext as _

register = template.Library()

default_msgs = {
        'regex_pattern': 'Pattern does not  match. %s',
        'min_length': 'Field has a min length of %s',
        'max_length': 'Field has a max length of %s',
        'equals': 'Field must equal %s',
        'custom': 'Not valid: %s',
        'invalid': 'Not valid: %s',
        'required': 'Field is required%s'}

@register.simple_tag
def validate_server(form, field):
    error_str = ""

    if field in form.errors:
        error_str = """<label for="id_%s" class="error" style="display: inline;">
            <div class="error-wrapper "><p class="error"> %s </p></div>
            </label>""" % (field, form.errors[field][0])
    return error_str


def custom_or_default(field, django, jquery):
    """Maps field error messages
    :param field: Field reference
    :param django: django naming
    :param jquery: jquery naming
    :return:
    """
    field[jquery] = getattr(field.field.error_messages, django, default_msgs[django])


def map_messages(field, validate_dict):
    """ Maps django messages to jquery messages
    :param field:
    :param validate_dict:
    :return:
    """
    # check field type restrictions
    if getattr(validate_dict['rules'][field.name], 'email', False):
        validate_dict['messages'][field.name]['email'] = field.field.error_messages['invalid']
    elif getattr(validate_dict['rules'][field.name], 'url', False):
        validate_dict['messages'][field.name]['url'] = field.field.error_messages['invalid']
    elif getattr(validate_dict['rules'][field.name], 'date', False):
        validate_dict['messages'][field.name]['date'] = field.field.error_messages['invalid']
    elif getattr(validate_dict['rules'][field.name], 'pattern', False):
        validate_dict['messages'][field.name]['pattern'] = field.field.error_messages['regex_pattern']

    # check rules
    if getattr(validate_dict['rules'][field.name], 'min_length', False):
        custom_or_default(validate_dict['messages'][field.name], 'min_length', 'minlength')
    if getattr(validate_dict['rules'][field.name], 'max_length', False):
        custom_or_default(validate_dict['messages'][field.name], 'max_length', 'maxlength')
    if getattr(validate_dict['rules'][field.name], 'equalTo', False):
        custom_or_default(validate_dict['messages'][field.name], 'equals', 'equalTo')
    if getattr(validate_dict['rules'][field.name], 'equalTo', False):
        custom_or_default(validate_dict['messages'][field.name], 'equals', 'equalTo')
    if getattr(validate_dict['rules'][field.name], 'custom', False):
        custom_or_default(validate_dict['messages'][field.name], 'custom', 'custom')
    if getattr(validate_dict['rules'][field.name], 'remote', False):
        custom_or_default(validate_dict['messages'][field.name], 'remote', 'remote')


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
        validate_dict['rules'][field.name] = field.field.widget.attrs["cls"]
        del field.field.widget.attrs["cls"]
        if 'remote' in field.field.widget.attrs:
            del field.field.widget.attrs["remote"]

        if 'custom' in field.field.widget.attrs:
            del field.field.widget.attrs["custom"]

        map_messages(field, validate_dict)


        validate_dict['messages'][field.name] = {}
        try:
            for key in field.field.error_messages:
                validate_dict['messages'][field.name][key] = unicode(field.field.error_messages[key])
        except:
            pass

        del field.field.widget.attrs['msg']

    validate_str += "<script type='text/javascript' src='/static/js/jquery.validate.min.js'></script>"
    validate_str += "<script type='text/javascript' src='/static/js/additional-methods.min.js'></script>"
    validate_str += "<script type='text/javascript'>"
    validate_str += "$(document).ready(function() {"
    validate_dict['success'] = "##function(label) { " + \
                               "    label.removeClass('error'); label.parent().removeClass('status-error'); label.remove();" + \
                               "}##"

    validate_dict['showErrors'] = "## function(errorMap, errorList) {" +\
        "this.defaultShowErrors();" + \
                                  "$('label.error').parent().addClass('status-error')" + \
                                  "}##"
    validate_str += "   $('#%s').validate(%s);" % (form_id, dumps(validate_dict, sort_keys=True))

    validate_str += "});"
    validate_str += '</script>'
    validate_str = validate_str.replace("\"##", "")
    validate_str = validate_str.replace("##\"", "")
    validate_str = validate_str.replace("\\\\", "\\")

    return validate_str
