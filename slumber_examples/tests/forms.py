from django import forms
from django.test import TestCase

from slumber import client
from slumber.forms import RemoteForeignKeyWidget

from slumber_examples.models import Order


class WidgetTest(TestCase):
    class Form(forms.Form):
        rfkw = forms.CharField(
            widget=RemoteForeignKeyWidget())

    def test_default_widget(self):
        form = WidgetTest.Form()
        self.assertEquals(form.as_p(),
            '''<p><label for="id_rfkw">Rfkw:</label> '''
                '''<input type="text" name="rfkw" id="id_rfkw" /></p>''')

    def test_default_widget_with_data(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        form = WidgetTest.Form(dict(rfkw=shop))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_rfkw">Rfkw:</label> '''
                '''<input type="text" name="rfkw" '''
                    '''value="" '''
                    '''id="id_rfkw" /></p>''')
