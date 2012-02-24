"""
    Contains widgets used for Slumber.
"""
from django import forms
from django.contrib.admin.widgets import AdminURLFieldWidget

from slumber.connector.api import _InstanceProxy, get_instance_from_url


class RemoteForeignKeyWidget(forms.TextInput):
    """A widget that allows the URL to be edited.
    """
    def render(self, name, value, **kw):
        if isinstance(value, basestring):
            return super(RemoteForeignKeyWidget, self).render(
                name, value, **kw)
        else:
            return super(RemoteForeignKeyWidget, self).render(
                name, value._url if value else None, **kw)


class RemoteForeignKeyField(forms.Field):
    """A simple widget that allows the URL for the remote object to be
    seen and edited.
    """
    def __init__(self, max_length=None, verify_exists=True, **kwargs):
        self.max_length = max_length
        self.verify_exists = verify_exists
        default = {'widget': RemoteForeignKeyWidget}
        default.update(kwargs)
        if default['widget'] == AdminURLFieldWidget:
            # We have to ignore a request for admin's broken widget
            default['widget'] = RemoteForeignKeyWidget
        super(RemoteForeignKeyField, self).__init__(**default)

    def clean(self, value):
        if not value:
            if self.required:
                raise forms.ValidationError('This field is required')
            return None
        elif isinstance(value, _InstanceProxy):
            return value
        else:
            instance = get_instance_from_url(value)
            try:
                instance._fetch_instance()._fetch_data()
            except AssertionError:
                raise forms.ValidationError("The remote object doesn't exist")
            return instance
