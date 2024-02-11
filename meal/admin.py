from django.contrib import admin

from .models import *

admin.site.register(Dish)
admin.site.register(Recipe)
admin.site.register(Product)
admin.site.register(Consumption)
admin.site.register(ProductInRecipe)
