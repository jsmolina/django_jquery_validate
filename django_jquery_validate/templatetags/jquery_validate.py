from django import template
from django import forms
import copy

register = template.Library()


class JqueryFormHelper(object):
    def preprocess_fields(self, form):
        for key in form.fields.keys():
            field_dict = {}
            form.fields[key].widget.attrs['msg'] = {}

            # emails
            if isinstance(form.fields[key], forms.fields.EmailField):
                field_dict['email'] = True

            elif isinstance(form.fields[key], forms.fields.DateField):
                field_dict['date'] = True

            elif isinstance(form.fields[key], forms.fields.TimeField):
                field_dict['time'] = True

            elif isinstance(form.fields[key], forms.fields.URLField):
                field_dict['url'] = True

            elif isinstance(form.fields[key], forms.fields.RegexField):
                field_dict['pattern'] = "##/" + \
                                        form.fields[key].regex.pattern + \
                                        "/i##"
            elif isinstance(form.fields[key], forms.fields.FloatField):
                field_dict['number'] = True

            if isinstance(form.fields[key], forms.fields.MultiValueField):
                for key2 in xrange(0, len(form.fields[key].fields)):
                    field_dict_copy = copy.deepcopy(field_dict)
                    rules_dict = self.check_attrs_rules(form.fields[key].fields[key2])
                    field_dict_copy.update(rules_dict)
                    form.fields[key].fields[key2].widget.attrs.update({'cls': field_dict_copy})
            else:
                rules_dict = self.check_attrs_rules(form.fields[key])
                field_dict.update(rules_dict)
                form.fields[key].widget.attrs.update({'cls': field_dict})

    def check_attrs_rules(self, field):
        """MultivalueWidgets Recursive nested fields support"""
        rules_dict = {}
        # Required
        if getattr(field, 'required', False) and field.required:
            rules_dict['required'] = field.required

        else:
            rules_dict['required'] = False

        # min length
        if getattr(field, 'min_length', False):
            if field.min_length is not None:
                rules_dict['minlength'] = field.min_length

        # max length
        if getattr(field, 'max_length', False):
            if field.max_length is not None:
                rules_dict['maxlength'] = field.max_length

        # field same value than...
        if 'equals' in field.widget.attrs:
            rules_dict['equalTo'] = "#%s" % field.widget.attrs['equals']
            equals_field = field.widget.attrs['equals'].replace('id_', '')

        if 'depends' in field.widget.attrs:
            rules_dict['depends'] = "#%s" % field.widget.attrs['depends']

        # custom JS validation function: use 'custom' attribute value on wiget
        # see http://stackoverflow.com/questions/241145/jquery-validate-plugin-how-to-create-a-simple-custom-rule
        if 'custom' in field.widget.attrs:
            custom = field.widget.attrs['custom']
            rules_dict[field.widget.attrs['custom']['method']] = custom['value']

        if 'remote' in field.widget.attrs:
            rules_dict['remote'] = {
                'url': field.widget.attrs['remote']['url']
            }

            if 'data' in field.widget.attrs['remote']:
                rules_dict['remote']['data'] = field.widget.attrs['remote']['data']

        return rules_dict


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
        error_str = '<label for="id_{0}" class="error" style="display: inline;">{1}</label>'.format(
            field, form.errors[field][0])
    return error_str


def custom_or_default(field, validate_dict, django, jquery, params=('',)):
    """Maps field error messages
    :param field: Field reference
    :param django: django naming
    :param jquery: jquery naming
    :return:
    """
    validate_dict[jquery] = unicode(field.field.error_messages.get(django, default_msgs[django] % params))


def map_messages(field, validate_dict):
    """ Maps django messages to jquery messages
    :param field:
    :param validate_dict:
    :return:
    """
    # check field type restrictions
    # take default message if not set
    if field.name not in validate_dict['rules']:
        return

    validate_dict['messages'][field.name] = {}
    if 'email' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'invalid', 'email', 'Invalid mail')
    elif 'url' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'invalid', 'url', 'Invalid url')
    elif 'date' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'invalid', 'date', 'Invalid date')
    elif 'pattern' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'regex_pattern', 'pattern', '')

    # check rules
    if 'minlength' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'min_length', 'minlength',
                          validate_dict['rules'][field.name]['minlength'])
    if 'maxlength' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'max_length', 'maxlength',
                          validate_dict['rules'][field.name]['maxlength'])
    if 'equalTo' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'equals', 'equalTo')
    if 'required' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'required', 'required')
    if 'custom' in field.field.widget.attrs:
        custom_method = field.field.widget.attrs['custom']['method']
        custom_or_default(field, validate_dict['messages'][field.name], 'custom', custom_method)
    if 'remote' in validate_dict['rules'][field.name]:
        custom_or_default(field, validate_dict['messages'][field.name], 'invalid', 'remote')


@register.simple_tag
def validate(form, form_id):
    """
    Validates form
    :param form:
    :param form_id:
    :return:
    """
    validate_str = ""
    helper = JqueryFormHelper()
    helper.preprocess_fields(form)
    validate_dict = {'onkeyup': False, 'rules': {}, 'messages': {}, "success": "", 'ignore': '.ignore'}

    for field in form:
        if isinstance(field.field, forms.fields.MultiValueField):
            for key2 in xrange(0, len(field.field.fields)):
                field2 = field.field.fields[key2]
                field2_name = "{0}_{1}".format(field.name, key2)
                validate_dict['rules'][field2_name] = field2.widget.attrs["cls"]
        else:
            validate_dict['rules'][field.name] = field.field.widget.attrs["cls"]
        map_messages(field, validate_dict)

        if 'msg' in field.field.widget.attrs:
            del field.field.widget.attrs['msg']

        if 'cls' in field.field.widget.attrs:
            del field.field.widget.attrs["cls"]

        if 'remote' in field.field.widget.attrs:
            del field.field.widget.attrs["remote"]

        if 'custom' in field.field.widget.attrs:
            del field.field.widget.attrs["custom"]
    validate_str += "<script type='text/javascript' src='/js/ext/jquery.validate.min.js'></script>"
    validate_str += "<script type='text/javascript' src='/js/ext/additional-methods.min.js'></script>"
    validate_str += "<script type='text/javascript'>"
    validate_str += "$(document).ready(function() {"
    validate_dict['success'] = "##function(label) { label.removeClass('error'); " \
                               "label.parent().removeClass('status-error'); label.remove();" + \
                               "}##"

    validate_dict['showErrors'] = "## function(errorMap, errorList) {" + \
                                  "this.defaultShowErrors();" + \
                                  "$('label.error').each(function() {" \
                                  " $(this).parent().addClass('status-error');" + \
                                  " $(this).attr('id', 'error_' + $(this).attr('for'));" + \
                                  "});}##"
    validate_dict['onfocusout'] = "## function(e) {" + \
                                  "this.element(e);" + \
                                  "}##"

    validate_str += "   $('#%s').validate(%s);" % (form_id, validate_dict)

    validate_str += "});"
    validate_str += '</script>'
    validate_str = validate_str.replace("\"##", "")
    validate_str = validate_str.replace("##\"", "")
    validate_str = validate_str.replace("'##", "")
    validate_str = validate_str.replace("##'", "")
    validate_str = validate_str.replace("\\\\", "\\")
    validate_str = validate_str.replace("u'", "'")
    validate_str = validate_str.replace("ufunction", "function")
    validate_str = validate_str.replace("True", "true")
    validate_str = validate_str.replace("False", "false")

    return validate_str
