"""
    Contains widgets used for Slumber.
"""
from django import forms


class RemoteForeignKeyWidget(forms.TextInput):
    """A widget that allows the URL to be edited.
    """
    def render(self, name, value, **kw):
        return super(RemoteForeignKeyWidget, self).render(
            name, value._url if value else None, **kw)

class RemoteForeignKeyField(forms.Field):
    """A simple widget that allows the URL for the remote object to be
    seen and edited.
    """
    def __init__(self, **kwargs):
        default = {'widget': RemoteForeignKeyWidget}
        default.update(kwargs)
        super(RemoteForeignKeyField, self).__init__(**default)
