from unittest import TestCase
from django import forms
from django.conf import settings
from .templatetags import jquery_validate
from . import *


class JqueryGenTest(TestCase):
    def setUp(self):
        try:
            settings.configure(DEBUG=True, USE_I18N=False, TEMPLATE_DEBUG=True,
                               TEMPLATE_DIRS=('/home/web-apps/myapp', '/home/web-apps/base'))
        except RuntimeError as e:
            pass

    def test_template_tag(self):
        """
        Tests that current validation if generating valid jquery_validate code
        """
        test = JqueryForm()
        trans = Trans("hello %s", "jordi")
        result = str(trans)
        self.assertEquals("hello jordi", result)

        RegisterForm = type("CommentForm", (forms.Form,), {
            'email': forms.EmailField(label="Your email",
                                      widget=forms.TextInput(attrs={'remote': {'url': "/user/mail-exists/",
                                                                               'message': "Email already taken"}})),
            'email2': forms.EmailField(label="Your email", required=True,
                                       widget=forms.TextInput(attrs={
                                           'depends': 'email2',
                                           'remote': {'url': "/user/mail-exists/", 'message': "Email already taken"},
                                           'custom': {'method': 'require_from_group', 'value': '[1,".mailgroup"]'}})),
            'password': forms.CharField(widget=forms.PasswordInput(attrs={'equals': 'id_password2'}),
                                        label="Choose a password",
                                        required=True,
                                        help_text="Use between 8 and 30. Oh! And use at least one number",
                                        max_length=30,
                                        min_length=8,
                                        error_messages=
                                        {
                                            'min_length': 'Should have at least 8',
                                            'max_length': 'Should have at most 30',
                                            'equals': 'Must be equal to password 2'}),
            'password2': forms.CharField(widget=forms.PasswordInput(), label="Confirm your password",
                                         required=True, help_text="One more time please...", max_length=30,
                                         min_length=8,
                                         error_messages={
                                             'min_length': 'Should have at least 8',
                                             'max_length': 'Should have at most 30',
                                             'equals': 'Must be equal to password 2'}),
            'country': forms.Select(),

            'test': forms.RegexField(regex=r'[a-zA-Z0-9]+', error_messages={"regex_pattern": 'Do not matches'}),
            'errors': {'country': ['Country is empty']}})
        form = RegisterForm()
        rendered = jquery_validate.validate(form, "myformid")
        self.assertRegexpMatches(rendered,
                                 "'email': {'required': true, 'remote': {'url': '/user/mail-exists/'}, 'email': true}")
        self.assertRegexpMatches(rendered, "\$\('#myformid'\).validate\({")
        self.assertRegexpMatches(rendered,
                                 "'password': {'minlength': 8, 'required': true, 'equalTo': '#id_password2', " +
                                 "'maxlength': 30}")
        self.assertRegexpMatches(rendered, "'password2': {'minlength': 8, 'required': true, 'maxlength': 30}")

        jquery_validate.validate_server(form, 'country')
