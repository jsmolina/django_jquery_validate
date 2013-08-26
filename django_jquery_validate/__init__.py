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

class Trans(object):
    def __init__(self, text, params):
        self.text = text
        self.params = params

    def __str__(self):
        return self.text % self.params
