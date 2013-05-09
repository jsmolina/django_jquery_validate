from django import forms


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

            # Required
            if getattr(self.fields[key], 'required', False) and self.fields[key].required:
                field_dict['required'] = self.fields[key].required

            else:
                field_dict['required'] = False

            # min length
            if getattr(self.fields[key], 'min_length', False):
                if self.fields[key].min_length is not None:
                    field_dict['minlength'] = self.fields[key].min_length

            # max length
            if getattr(self.fields[key], 'max_length', False):
                if self.fields[key].max_length is not None:
                    field_dict['maxlength'] = self.fields[key].max_length

            # field same value than...
            if 'equals' in self.fields[key].widget.attrs:
                field_dict['equalTo'] = "#%s" % self.fields[key].widget.attrs['equals']
                equals_field = self.fields[key].widget.attrs['equals'].replace('id_', '')
                # equals_name = self.fields[equals_field].label

            if 'depends' in self.fields[key].widget.attrs:
                field_dict['depends'] = "#%s" % self.fields[key].widget.attrs['depends']

            # custom JS validation function: use 'custom' attribute value on wiget
            # see http://stackoverflow.com/questions/241145/jquery-validate-plugin-how-to-create-a-simple-custom-rule
            if 'custom' in self.fields[key].widget.attrs:
                custom = self.fields[key].widget.attrs['custom']
                field_dict[self.fields[key].widget.attrs['custom']['method']] = custom['value']

            if 'remote' in self.fields[key].widget.attrs:
                field_dict['remote'] = self.fields[key].widget.attrs['remote']['url']

            self.fields[key].widget.attrs.update({'cls': field_dict})


class Trans(object):
    def __init__(self, text, params):
        self.text = text
        self.params = params

    def __str__(self):
        return self.text % self.params
