from django.db import models


class Pizza(models.Model):
    name = models.fields.CharField(max_length=200, unique=True, blank=False)
    for_sale = models.fields.BooleanField()
    max_extra_toppings = models.fields.IntegerField(null=True, blank=False)

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
