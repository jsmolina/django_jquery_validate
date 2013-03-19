from django.utils.translation import ugettext_lazy as _
from django import forms
from simplejson import dumps
from django.forms import Form

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
            return _("%s %s %s") % (error_start, arg, error_end)

        for key in self.fields.keys():
            field_dict = {}
            self.fields[key].widget.attrs['msg'] = {}

            # Required
            if hasattr(self.fields[key], 'required'):
                field_dict['required'] = True
                self.fields[key].widget.attrs['msg']['required'] = get_error_tags('required')
            else:
                field_dict['required'] = False

            # min length
            if hasattr(self.fields[key], 'min_length'):
                if self.fields[key].min_length != None:
                    field_dict['minlength'] = self.fields[key].min_length
                    self.fields[key].widget.attrs['msg']['minlength'] = "%s" % (
                        get_error_tags("%s characters minimum") % self.fields[key].min_length)

            # max length
            if hasattr(self.fields[key], 'max_length'):
                if self.fields[key].max_length != None:
                    field_dict['maxlength'] = self.fields[key].max_length
                    self.fields[key].widget.attrs['msg']['maxlength'] = "%s" % (
                        get_error_tags("%s characters maximum") % self.fields[key].max_length)


            # emails
            if self.fields[key].__class__.__name__ == 'EmailField':
                field_dict['email'] = True
                self.fields[key].widget.attrs['msg']['email'] = "%s" % get_error_tags("Invalid email address")

            # field same value than...
            if 'equals' in self.fields[key].widget.attrs:
                field_dict['equalTo'] = "#%s" % self.fields[key].widget.attrs['equals']
                equals_field = self.fields[key].widget.attrs['equals'].replace('id_', '')
                equals_name = self.fields[equals_field].label
                self.fields[key].widget.attrs['msg']['equalTo'] = get_error_tags("Must be equal to %s") % equals_name

            """ if depends on checkbox is checked e.g:
             depends: function(element) {
               return $("#contactform_email:checked")
             }
            """
            if 'depends' in self.fields[key].widget.attrs:
                field_dict['depends'] = "#%s" % self.fields[key].widget.attrs['depends']

            # custom JS validation function: use 'custom' attribute value on wiget
            # see http://stackoverflow.com/questions/241145/jquery-validate-plugin-how-to-create-a-simple-custom-rule
            if 'custom' in self.fields[key].widget.attrs:
                field_dict[self.fields[key].widget.attrs['custom']] = True

            self.fields[key].widget.attrs.update({'cls': dumps(field_dict)})

    def render_field(self, field):
        """

        :param field:
        """
        pass

    def as_table(self):
        """

        Returns this form rendered as HTML
        """
        return self._html_output(
            normal_row = u'<div%(html_class_attr)s><h2><span class="num">.</span>'+\
                         u'<span class="desc">%(label)s</span></h2>'+\
                         u'%(field)s',
            error_row = u'<label for="id_password2" class="error"><div class="error-wrapper "><p class="error">%s </p></div></label>',
            row_ender = u'</div>',
            help_text_html = u'<p class="desc">%s</p>',
            errors_on_separate_row=False)

