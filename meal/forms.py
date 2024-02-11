from django import forms
from .models import *


class DishForm(forms.Form):
    dish_id = forms.ModelChoiceField(label="Блюдо", queryset=Dish.objects.all())


class AddProductToRecipe(forms.Form):
    recipe_id = forms.ModelChoiceField(label="Рецепт", queryset=Recipe.objects.all())
    product_id = forms.ModelChoiceField(label="Продукт", queryset=Product.objects.all())
    weight = forms.IntegerField(label="Вес продукта", max_value=1000, min_value=1)


class ShowRecipesWithoutProduct(forms.Form):
    product_id = forms.ModelChoiceField(label="Продукт", queryset=Product.objects.all())


class CookRecipe(forms.Form):
    recipe_id = forms.ModelChoiceField(label="Рецепт", queryset=Recipe.objects.all())
