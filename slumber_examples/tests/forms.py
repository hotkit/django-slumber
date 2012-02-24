from django import forms
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.test import TestCase

from slumber import client
from slumber.connector.api import get_instance_from_url
from slumber.forms import RemoteForeignKeyField

from slumber_examples.models import Order


class WidgetTest(TestCase):
    class Form(forms.Form):
        rfk = RemoteForeignKeyField(required=True)
    class OptionalForm(forms.Form):
        rfk = RemoteForeignKeyField(required=False)
    class ModelForm(forms.ModelForm):
        class Meta:
            model = Order
    class AdminForm(forms.Form):
        rfk = RemoteForeignKeyField(widget=AdminURLFieldWidget)

    def test_default_formfield(self):
        form = WidgetTest.Form()
        self.assertEquals(form.as_p(),
            '''<p><label for="id_rfk">Rfk:</label> '''
                '''<input type="text" name="rfk" id="id_rfk" /></p>''')

    def test_empty_form_submission_with_required_field(self):
        form = WidgetTest.Form(dict(rfk=''))
        self.assertFalse(form.is_valid())
        self.assertEquals(form.as_p(),
            '''<ul class="errorlist"><li>This field is required</li></ul>\n'''
            '''<p><label for="id_rfk">Rfk:</label> '''
                '''<input type="text" name="rfk" id="id_rfk" /></p>''')

    def test_empty_form_submission_with_optional_field(self):
        form = WidgetTest.OptionalForm(dict(rfk=''))
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['rfk'])

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

    def test_given_bad_url(self):
        form = WidgetTest.Form(dict(rfk=
            'http://localhost:8000/slumber/slumber_examples/Shop/2/data/'))
        self.assertFalse(form.is_valid())

    def test_model_form(self):
        form = WidgetTest.ModelForm()
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" id="id_shop" /></p>''')

    def test_model_form_submission_with_object(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        form = WidgetTest.ModelForm(dict(shop=shop))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')
        self.assertEquals(type(form.fields['shop']), RemoteForeignKeyField)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')
        self.assertEquals(form.cleaned_data['shop'].id, shop.id)

    def test_model_form_submission_with_url(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        form = WidgetTest.ModelForm(dict(shop=shop._url))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')
        self.assertEquals(type(form.fields['shop']), RemoteForeignKeyField)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')

    def test_model_form_submission_with_instance_get_instance(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        shop_from_url = get_instance_from_url(shop._url)
        form = WidgetTest.ModelForm(dict(shop=shop_from_url))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')
        self.assertEquals(type(form.fields['shop']), RemoteForeignKeyField)
        self.assertTrue(form.is_valid())
        self.assertEquals(unicode(form.cleaned_data['shop']), unicode(shop))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')

    def test_model_form_with_order(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        order = Order(shop=shop)
        order.save()
        form = WidgetTest.ModelForm(instance=order)
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')

    def test_model_form_with_order_from_database(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        order = Order(shop=shop)
        order.save()
        order_db = Order.objects.get(pk=order.pk)
        form = WidgetTest.ModelForm(instance=order_db)
        self.assertEquals(form.as_p(),
            '''<p><label for="id_shop">Shop:</label> '''
                '''<input type="text" name="shop" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_shop" /></p>''')

    def test_admin_form_with_order(self):
        shop = client.slumber_examples.Shop.create(
            name='Shop', slug='shop')
        form = WidgetTest.AdminForm(dict(rfk=shop))
        self.assertEquals(form.as_p(),
            '''<p><label for="id_rfk">Rfk:</label> '''
                '''<input type="text" name="rfk" '''
                    '''value="http://localhost:8000/slumber/slumber_examples/Shop/data/1/" '''
                    '''id="id_rfk" /></p>''')
