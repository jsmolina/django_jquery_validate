from unittest import TestCase
from .. import JqueryForm
from django import forms
from django.conf import settings
from simplejson import dumps, loads
from django.forms import Form
from ..templatetags import jquery_validate



class FormGen(TestCase):
    def setUp(self):
        try:
            settings.configure(DEBUG=True, USE_I18N=False, TEMPLATE_DEBUG=True,
                           TEMPLATE_DIRS=('/home/web-apps/myapp', '/home/web-apps/base'))
        except RuntimeError as e:
            pass

    def test_jquery_prepare(self):
        """
        This test validates jquery preparation of module
        """
        CommentForm = type("CommentForm", (JqueryForm,), {
            'email': forms.EmailField(min_length=2, max_length=5),
            'url': forms.URLField(),
        })
        form = CommentForm()

        for key in form.fields.keys():
            msg = form.fields[key].widget.attrs['msg']
            cls = loads(form.fields[key].widget.attrs['cls'])

            if key is "email":
                self.assertTrue(cls['email'])
                self.assertTrue(cls['required'])
                self.assertEquals(cls['minlength'], 2)
                self.assertEquals(cls['maxlength'], 5)
                self.assertIn('minlength', msg)
                self.assertIn('required', msg)
                self.assertIn('maxlength', msg)
            elif key is "url":
                self.assertTrue(cls['url'])

    def test_jquery_prepare_with_remote(self):
        """
        Tests remote requests
        """
        RegisterForm = type("CommentForm", (JqueryForm,), {
            'email': forms.EmailField(label="Your email", required=True,
                                      widget=forms.TextInput(attrs={
                                          'remote': {'url': "/user/mail-exists/", 'message': "Email already taken"}})),
            'test' : forms.RegexField(regex=r'[a-zA-Z0-9]+'),
            'password': forms.CharField(widget=forms.PasswordInput(attrs={'equals': 'id_password2'}),
                                        label="password",
                                        required=True,
                                        help_text="8 to 30",
                                        max_length=30, min_length=8),
            'password2': forms.CharField(widget=forms.PasswordInput(), label="Confirm your password",
                                         required=True, help_text="One more time please...", max_length=30,
                                         min_length=8),
            'country': forms.Select()
        })
        form = RegisterForm()

        for key in form.fields.keys():
            msg = form.fields[key].widget.attrs['msg']
            cls = loads(form.fields[key].widget.attrs['cls'])

            if key is "email":
                self.assertTrue(cls['email'])
                self.assertEquals(cls['remote'], "/user/mail-exists/")
                self.assertTrue(cls['required'])
            elif key is "password":
                self.assertEquals(cls['equalTo'], "#id_password2")
                self.assertTrue(cls['required'])
                self.assertEquals(cls['minlength'], 8)
                self.assertEquals(cls['maxlength'], 30)
            elif key is "password2":
                self.assertTrue(cls['required'])
                self.assertEquals(cls['minlength'], 8)
                self.assertEquals(cls['maxlength'], 30)
            elif key is "test":
                self.assertEquals(cls['pattern'], "##/^[a-zA-Z0-9]+$/i##")

    def test_template_tag(self):
        """
        Tests that current validation if generating valid jquery_validate code
        """
        RegisterForm = type("CommentForm", (JqueryForm,), {
            'email': forms.EmailField(label="Your email", required=True,
                                      widget=forms.TextInput(attrs={
                                          'remote': {'url': "/user/mail-exists/", 'message': "Email already taken"}})),
            'password': forms.CharField(widget=forms.PasswordInput(attrs={'equals': 'id_password2'}),
                                        label="Choose a password",
                                        required=True,
                                        help_text="Use between 8 and 30. Oh! And use at least one number",
                                        max_length=30, min_length=8),
            'password2': forms.CharField(widget=forms.PasswordInput(), label="Confirm your password",
                                         required=True, help_text="One more time please...", max_length=30,
                                         min_length=8),
            'country': forms.Select(),

            'test' : forms.RegexField(regex=r'[a-zA-Z0-9]+'),
        })
        form = RegisterForm()
        rendered = jquery_validate.validate(form, "myformid")

        self.assertRegexpMatches(rendered, '"email": {"email": true, "remote": "/user/mail-exists/", "required": true}')
        self.assertRegexpMatches(rendered, "\$\('#myformid'\).validate\({")
        self.assertRegexpMatches(rendered, '"password": {"equalTo": "#id_password2", "maxlength": 30, "minlength": 8, "required": true}')
        self.assertRegexpMatches(rendered, '"password2": {"maxlength": 30, "minlength": 8, "required": true}')
        self.assertRegexpMatches(rendered, '"test": {"pattern"')

