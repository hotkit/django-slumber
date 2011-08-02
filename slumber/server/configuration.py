from django.core.urlresolvers import reverse

def get_slumber_root():
    return reverse('slumber.server.views.get_applications')#settings.SLUMBER_ROOT