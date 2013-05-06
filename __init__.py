from django import forms


class JqueryForm(forms.Form):
    """
    BaseForm for applying jquery validation
    """
    default_msgs = {
        'regex_pattern': 'Pattern does not  match. %s',
        'min_length': 'Field has a min length of %s',
        'max_length': 'Field has a max length of %s',
        'equals': 'Field must equal %s',
        'custom': 'Not valid: %s',
        'invalid': 'Not valid: %s',
        'required': 'Field is required%s'}

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
                self.fields[key].widget.attrs['msg']['email'] = get_error_tags(
                    self.fields[key],
                    "invalid")

            elif isinstance(self.fields[key], forms.fields.DateField):
                field_dict['date'] = True
                self.fields[key].widget.attrs['msg']['date'] = get_error_tags(
                    self.fields[key],
                    "invalid")

            elif isinstance(self.fields[key], forms.fields.URLField):
                field_dict['url'] = True
                self.fields[key].widget.attrs['msg']['url'] = get_error_tags(
                    self.fields[key],
                    "invalid")

            elif isinstance(self.fields[key], forms.fields.RegexField):
                field_dict['pattern'] = "##/" + \
                                        self.fields[key].regex.pattern + \
                                        "/i##"
                self.fields[key].widget.attrs['msg']['pattern'] = get_error_tags(
                    self.fields[key],
                    "regex_pattern")

            # Required
            if getattr(self.fields[key], 'required', False) and self.fields[key].required:
                field_dict['required'] = self.fields[key].required
                self.fields[key].widget.attrs['msg']['required'] = get_error_tags(
                    self.fields[key],
                    "required")
            else:
                field_dict['required'] = False

            # min length
            if getattr(self.fields[key], 'min_length', False):
                if self.fields[key].min_length is not None:
                    field_dict['minlength'] = self.fields[key].min_length
                    self.fields[key].widget.attrs['msg']['minlength'] = get_error_tags(
                        self.fields[key],
                        "min_length",
                        field_dict['minlength'])

            # max length
            if getattr(self.fields[key], 'max_length', False):
                if self.fields[key].max_length is not None:
                    field_dict['maxlength'] = self.fields[key].max_length
                    self.fields[key].widget.attrs['msg']['maxlength'] = "%s" % \
                        get_error_tags(
                            self.fields[key],
                            "max_length",
                            field_dict['maxlength'])

            # field same value than...
            if 'equals' in self.fields[key].widget.attrs:
                field_dict['equalTo'] = "#%s" % self.fields[key].widget.attrs['equals']
                equals_field = self.fields[key].widget.attrs['equals'].replace('id_', '')
                # equals_name = self.fields[equals_field].label
                self.fields[key].widget.attrs['msg']['equalTo'] = get_error_tags(
                    self.fields[key],
                    "equals")

            if 'depends' in self.fields[key].widget.attrs:
                field_dict['depends'] = "#%s" % self.fields[key].widget.attrs['depends']

            # custom JS validation function: use 'custom' attribute value on wiget
            # see http://stackoverflow.com/questions/241145/jquery-validate-plugin-how-to-create-a-simple-custom-rule
            if 'custom' in self.fields[key].widget.attrs:
                custom = self.fields[key].widget.attrs['custom']
                field_dict[self.fields[key].widget.attrs['custom']['method']] = custom['value']

            if 'custom' in self.fields[key].error_messages:
                self.fields[key].widget.attrs['msg'][custom['method']] = get_error_tags(
                    self.fields[key],
                    "custom")

            if 'remote' in self.fields[key].widget.attrs:
                field_dict['remote'] = self.fields[key].widget.attrs['remote']['url']
                self.fields[key].widget.attrs['msg']['remote'] = get_error_tags(
                    self.fields[key].widget.attrs['remote']['message'])

            self.fields[key].widget.attrs.update({'cls': field_dict})
