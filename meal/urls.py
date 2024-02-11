from django.urls import path

from meal.views import *


urlpatterns = [
    path('', index, name='home_page'),
    path('dish/consumption/', dish_consumption, name='dish_consumption'),
    path('product/recipe/', product_to_recipe, name='product_to_recipe'),
    path('recipe/analytic/', recipe_analytic, name='recipe_analytic'),
    path('hello/', hello_name),
]

