from django.db import models


class Pizza(models.Model):
    name = models.fields.CharField(max_length=200, unique=True, blank=False)
    for_sale = models.fields.BooleanField()

    def __unicode__(self):
        return self.name

