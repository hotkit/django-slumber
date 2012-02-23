"""
    Contains widgets used for Slumber.
"""
from django import forms


class RemoteForeignKeyWidget(forms.TextInput):
    """A simple widget that allows the URL for the remote object to be
    seen and edited.
    """
    pass
