"""
    Contains widgets used for Slumber.
"""
from django import forms

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
        super(RemoteForeignKeyField, self).__init__(**default)

    def prep_value(self, value):
        """This prepares the value under later versions of Django so that if
        another widget is used we still get the URL.
        """
        # This needs to be a method as that's what Django has designed
        # pylint: disable=R0201
        if isinstance(value, basestring):
            return value
        else:
            return value._url if value else None

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
