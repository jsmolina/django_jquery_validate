from django import forms

JqueryForm = forms.Form


class Trans(object):
    def __init__(self, text, params):
        self.text = text
        self.params = params

    def __str__(self):
        return self.text % self.params
