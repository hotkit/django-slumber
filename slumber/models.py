"""
    Integration between Slumber and Django models.
"""
from django.models import URLField


class RemoteForeignKey(URLField):
    pass
