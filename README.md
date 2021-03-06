django_jquery_validate
======================

A simple django app featuring automatic jquery validation code.

Based on sample from snarfu.com

What's new
==========
Converted JqueryForm to class decorator, to simplify usage.

Usage
=====
First, enable on settings.py the app.
NEW! You just create a new form, using normal django forms, no need of inheritance.
```python
 class RegisterForm(forms.Form):
    email = forms.EmailField(
        min_length=8, max_length=20,
        label="Type your email so we can confirm you're there",
        required=True,
        widget=forms.TextInput(
            attrs={'remote': {'url': "/user/mail-exists", 'message': "Email already taken"}}),
        error_messages={"min_length": Trans(
            _('Use %(min)s and %(max)s characters with at least one number'),
            {'min': 8, 'max': 20}
        )}),
    name = forms.RegexField(regex=r'[a-zA-Z0-9]+', error_messages={
        "invalid": "Use only alphanumeric characters", })
```

You could also create a field which is required only if a checkbox is enabled in two ways: Adding 'ignore' 
class on checkbox, or creating a custom JS code:
```python
field.widget.attrs['custom'] = {
    'method': 'required',
    'value': "##function (element) {" +
 	"if($(\"#id_" + 'myCheckbox_' + id + "\").is(\":checked\")) {" +
		" return true;} else { return false;}"
		"}##"}

```

* NOTE: If you have something parametrized, you could use provided Trans class.
* NOTE2: Remote supports sending 'data' param, allowing sending additional data (e.g. another field) to server.

```python
widget=forms.TextInput(
            attrs={
                'remote': {
                    'url': "/user/name-exists/",
                    'data': {'id': '##$("#id_id").val()##'}
                }
            }
        ),
```
Then in template, you just specify the place where you want to have the jquery code for templatetag:
```python
{% load jquery_validate %}{% validate form "signup-form" %}
```

Showing server-side validation errors in template is easy (e.g. image size for a file):
```python 
 {% validate_server form "fieldname" %}
```
Which can be forced from view:
```python 
  if form.is_valid():
    form._errors["fieldname"] = ErrorList([u"Invalid image size."])
```

Test
=====
Just execute nosetests in django_jquery_validate

Additional info
===============
If you use multilingual and you see a functional__proxy inside your html code, there is a trick to force the string representation:
ugettext_lazy("Hello").encode('utf-8')
