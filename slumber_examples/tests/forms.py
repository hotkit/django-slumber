from django import forms
from django.test import TestCase

from slumber import client
from slumber.forms import RemoteForeignKeyField

from slumber_examples.models import Order


class WidgetTest(TestCase):
    class Form(forms.Form):
        rfk = RemoteForeignKeyField()

    def test_default_formfield(self):
        form = WidgetTest.Form()
        self.assertEquals(form.as_p(),
            '''<p><label for="id_rfk">Rfk:</label> '''
                '''<input type="text" name="rfk" id="id_rfk" /></p>''')

    def test_default_widget_with_data(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        form = WidgetTest.Form(dict(rfk=shop))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_rfk">Rfk:</label> '''
                '''<input type="text" name="rfk" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_rfk" /></p>''')

    def test_default_widget_with_submit_data(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        form = WidgetTest.Form(dict(rfk=shop._url))
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['rfk'].id, shop.id)
