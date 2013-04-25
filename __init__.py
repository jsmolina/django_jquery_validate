from django import forms
from simplejson import dumps


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

        def get_error_tags(arg):
            error_start = "<div class='error-wrapper '><p class='error'>"
            error_end = "</p></div>"
            return "%s %s %s" % (error_start, arg, error_end)

        for key in self.fields.keys():
            field_dict = {}
            self.fields[key].widget.attrs['msg'] = {}


            # emails
            if isinstance(self.fields[key], forms.fields.EmailField):
                field_dict['email'] = True
                self.fields[key].widget.attrs['msg']['email'] = "%s" % get_error_tags(self.fields[key].error_messages["invalid"])

            elif isinstance(self.fields[key], forms.fields.DateField):
                field_dict['date'] = True
                self.fields[key].widget.attrs['msg']['date'] = "%s" % get_error_tags(self.fields[key].error_messages["invalid"])

            elif isinstance(self.fields[key], forms.fields.URLField):
                field_dict['url'] = True
                self.fields[key].widget.attrs['msg']['url'] = "%s" % get_error_tags(self.fields[key].error_messages["invalid"])

            elif isinstance(self.fields[key], forms.fields.RegexField):
                field_dict['pattern'] = "##/" + self.fields[key].regex.pattern + "/i##"
                self.fields[key].widget.attrs['msg']['pattern'] = "%s" % get_error_tags(self.fields[key].error_messages["regex_pattern"])

            # Required
            if getattr(self.fields[key], 'required', False) and self.fields[key].required:
                field_dict['required'] = self.fields[key].required
                self.fields[key].widget.attrs['msg']['required'] = "%s" % get_error_tags(self.fields[key].error_messages["required"])
            else:
                field_dict['required'] = False

            # min length
            if getattr(self.fields[key], 'min_length', False):
                if self.fields[key].min_length != None:
                    field_dict['minlength'] = self.fields[key].min_length
                    self.fields[key].widget.attrs['msg']['minlength'] =  "%s" % get_error_tags(self.fields[key].error_messages["min_length"])

            # max length
            if getattr(self.fields[key], 'max_length', False):
                if self.fields[key].max_length != None:
                    field_dict['maxlength'] = self.fields[key].max_length
                    self.fields[key].widget.attrs['msg']['maxlength'] = "%s" % get_error_tags(self.fields[key].error_messages["max_length"])

            # field same value than...
            if 'equals' in self.fields[key].widget.attrs:
                field_dict['equalTo'] = "#%s" % self.fields[key].widget.attrs['equals']
                equals_field = self.fields[key].widget.attrs['equals'].replace('id_', '')
                # equals_name = self.fields[equals_field].label
                self.fields[key].widget.attrs['msg']['equalTo'] = get_error_tags(self.fields[key].error_messages["equals"])

            if 'depends' in self.fields[key].widget.attrs:
                field_dict['depends'] = "#%s" % self.fields[key].widget.attrs['depends']

            # custom JS validation function: use 'custom' attribute value on wiget
            # see http://stackoverflow.com/questions/241145/jquery-validate-plugin-how-to-create-a-simple-custom-rule
            if 'custom' in self.fields[key].widget.attrs:
                custom = self.fields[key].widget.attrs['custom']
                field_dict[self.fields[key].widget.attrs['custom']['method']] = custom['value']

            if 'custom' in self.fields[key].error_messages:
                self.fields[key].widget.attrs['msg'][custom['method']] = "%s" % get_error_tags(
                    self.fields[key].error_messages["custom"])

            if 'remote' in self.fields[key].widget.attrs:
                field_dict['remote'] = self.fields[key].widget.attrs['remote']['url']
                self.fields[key].widget.attrs['msg']['remote'] = get_error_tags(self.fields[key].widget.attrs['remote']['message'])

            self.fields[key].widget.attrs.update({'cls': field_dict})


