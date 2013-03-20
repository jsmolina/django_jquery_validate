django_jquery_validate
======================

A simple django app featuring automatic jquery validation code.

Based on sample from snarfu.com

Usage
=====
First, enable on settings.py the app.
You just create a new form, using normal django forms, but extending JqueryForm instead of Form:
```python
 class RegisterForm(JqueryForm):
    email = forms.EmailField(label="Type your email so we can confirm you're there", required=True, widget=forms.TextInput(attrs={
        'remote': {'url': "/user/mail-exists", 'message': "Email already taken"}}))
```

Then in template, you just specify the place where you want to have the jquery code for templatetag:
```python
{% load jquery_validate %}{% validate form "signup-form" %}
```
