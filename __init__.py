from django import forms
import copy


class JqueryForm(forms.Form):
    """
    BaseForm for applying jquery validation
    """


    def __init__(self, *args, **kwargs):
        """
        BaseForm for jquery_validate
        :param args:
        :param kwargs:
        :return:
        """
        super(JqueryForm, self).__init__(*args, **kwargs)

        def get_error_tags(arg, message_id=None, param=""):
            error_start = "<div class='error-wrapper '><p class='error'>"
            error_end = "</p></div>"
            if isinstance(arg, dict):
                message = arg.error_messages.get(
                    message_id,
                    self.default_msgs[message_id] % param)
            else:
                message = arg

            return "%s %s %s" % (error_start, message, error_end)

        for key in self.fields.keys():
            field_dict = {}
            self.fields[key].widget.attrs['msg'] = {}

            # emails
            if isinstance(self.fields[key], forms.fields.EmailField):
                field_dict['email'] = True

            elif isinstance(self.fields[key], forms.fields.DateField):
                field_dict['date'] = True

            elif isinstance(self.fields[key], forms.fields.URLField):
                field_dict['url'] = True

            elif isinstance(self.fields[key], forms.fields.RegexField):
                field_dict['pattern'] = "##/" + \
                                        self.fields[key].regex.pattern + \
                                        "/i##"

            if isinstance(self.fields[key], forms.fields.MultiValueField):
                for key2 in xrange(0, len(self.fields[key].fields)):
                    field_dict_copy = copy.deepcopy(field_dict)
                    rules_dict = self.check_attrs_rules(self.fields[key].fields[key2])
                    field_dict_copy.update(rules_dict)
                    self.fields[key].fields[key2].widget.attrs.update({'cls': field_dict_copy})
            else:
                rules_dict = self.check_attrs_rules(self.fields[key])
                field_dict.update(rules_dict)
                self.fields[key].widget.attrs.update({'cls': field_dict})

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


class Trans(object):
    def __init__(self, text, params):
        self.text = text
        self.params = params

    def __str__(self):
        return self.text % self.params
