from django.contrib import admin
from slumber_examples.models import (Pizza, PizzaCrust, PizzaPrice,
    PizzaSizePrice, Shop)


admin.site.register(Pizza)
admin.site.register(PizzaCrust)
admin.site.register(PizzaPrice)
admin.site.register(PizzaSizePrice)
admin.site.register(Shop)
