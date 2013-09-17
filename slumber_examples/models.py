from django.db import models

from slumber.fields import RemoteForeignKey


class Shop(models.Model):
    name = models.fields.CharField(max_length=200)
    slug = models.fields.CharField(max_length=20, unique=True, blank=False)
    active = models.fields.NullBooleanField()

    @property
    def web_address(self):
        return 'http://www.example.com/%s/' % self.slug

    def __unicode__(self):
        return self.name


class Pizza(models.Model):
    name = models.fields.CharField(max_length=200, unique=True, blank=False)
    for_sale = models.fields.BooleanField()
    max_extra_toppings = models.fields.IntegerField(null=True, blank=False)
    exclusive_to = models.ForeignKey(Shop, null=True,
        help_text="If specified then this pizza is exclusive to the specified shop")

    def __unicode__(self):
        return self.name


class PizzaPrice(models.Model):
    pizza = models.ForeignKey(Pizza, null=False, related_name='prices')
    date = models.fields.DateField()


PIZZA_SIZES = (
    ('s', 'Small'),
    ('m', 'Medium'),
    ('l', 'Large'),
)

class PizzaSizePrice(models.Model):
    price = models.ForeignKey(PizzaPrice, null=False, related_name='amounts')
    amount = models.fields.DecimalField(decimal_places=2, max_digits=8)
    size = models.CharField(max_length=1, choices=PIZZA_SIZES)

    class Meta:
        unique_together=[('price', 'size')]


class Profile(models.Model):
    user = models.ForeignKey('auth.User',
        null=False, blank=False)


class Order(models.Model):
    shop = RemoteForeignKey(null=False,
        model_url='slumber://pizzas/slumber_examples/Shop/')
    nested = RemoteForeignKey(null=True, blank=True,
        model_url='slumber://pizzas/slumber_ex_shop/NestedModel')


class PizzaCrust(models.Model):
    code = models.fields.CharField(primary_key = True, unique = True, max_length = 3)
    full_name = models.fields.CharField(max_length = 200)
