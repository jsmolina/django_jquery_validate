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
            if self.fields[key].__class__.__name__ == 'EmailField':
                field_dict['email'] = True
                self.fields[key].widget.attrs['msg']['email'] = "%s" % get_error_tags(
                    self.fields[key].error_messages["invalid"])

            elif self.fields[key].__class__.__name__ == 'DateField':
                field_dict['date'] = True
                self.fields[key].widget.attrs['msg']['date'] = "%s" % get_error_tags(
                    self.fields[key].error_messages["invalid"])

            elif self.fields[key].__class__.__name__ == 'URLField':
                field_dict['url'] = True
                self.fields[key].widget.attrs['msg']['url'] = "%s" % get_error_tags(
                    self.fields[key].error_messages["invalid"])
            elif self.fields[key].__class__.__name__ == 'RegexField':
                field_dict['pattern'] = "##/^" + self.fields[key].regex.pattern + "$/i##"
                self.fields[key].widget.attrs['msg']['pattern'] = "%s" % get_error_tags(
                    self.fields[key].error_messages["invalid"])

            # Required
            if hasattr(self.fields[key], 'required'):
                field_dict['required'] = self.fields[key].required
                self.fields[key].widget.attrs['msg']['required'] = get_error_tags('required')
            else:
                field_dict['required'] = False

            # min length
            if hasattr(self.fields[key], 'min_length'):
                if self.fields[key].min_length != None:
                    field_dict['minlength'] = self.fields[key].min_length
                    if "min_length" in self.fields[key].error_messages:
                        self.fields[key].widget.attrs['msg']['minlength'] = "%s" % get_error_tags(
                            self.fields[key].error_messages["min_length"])

            # max length
            if hasattr(self.fields[key], 'max_length'):
                if self.fields[key].max_length != None:
                    field_dict['maxlength'] = self.fields[key].max_length

                    if "max_length" in self.fields[key].error_messages:
                        self.fields[key].widget.attrs['msg']['maxlength'] = "%s" % get_error_tags(
                            self.fields[key].error_messages["max_length"])


            # field same value than...
            if 'equals' in self.fields[key].widget.attrs:
                field_dict['equalTo'] = "#%s" % self.fields[key].widget.attrs['equals']
                equals_field = self.fields[key].widget.attrs['equals'].replace('id_', '')
                equals_name = self.fields[equals_field].label
                if "equals" in self.fields[key].error_messages:
                    self.fields[key].widget.attrs['msg']['equalTo'] = "%s" % get_error_tags(
                        self.fields[key].error_messages["equals"])

            if 'depends' in self.fields[key].widget.attrs:
                field_dict['depends'] = "#%s" % self.fields[key].widget.attrs['depends']

            if 'custom' in self.fields[key].widget.attrs:
                custom = self.fields[key].widget.attrs['custom']
                field_dict[self.fields[key].widget.attrs['custom']['method']] = custom['value']
                if 'custom' in self.fields[key].error_messages:
                    self.fields[key].widget.attrs['msg'][custom['method']] = "%s" % get_error_tags(
                                self.fields[key].error_messages["custom"])


            if 'remote' in self.fields[key].widget.attrs:
                field_dict['remote'] = self.fields[key].widget.attrs['remote']['url']
                self.fields[key].widget.attrs['msg']['remote'] = get_error_tags(
                    self.fields[key].widget.attrs['remote']['message'])

            self.fields[key].widget.attrs.update({'cls': dumps(field_dict, sort_keys=True)})


