from django.shortcuts import render

from cookbook.tasks import *
from .models import *
from .forms import *


def index(request):
    product = Product.objects.all()
    dish = Dish.objects.all()
    form = DishForm()
    dish_selected = request.GET.dict()
    print('dish_selected: ', dish_selected)
    context = {"product": product, "dish": dish, "form": form, "dish_selected": dish_selected}
    return render(request, "meal/index.html", context)


def dish_consumption(request):
    form = CookRecipe()
    recipe_selected = request.GET.dict()
    print('recipe_selected: ', recipe_selected)
    if recipe_selected:
        recipe_id = int(recipe_selected['recipe_id'])
        # user = request.user
        form_request = request.GET.dict()
        print('получено из формы: ', form_request)
        task = cook_recipe.delay(recipe_id)
        result = task.get()
        print('task.get(): ', result, 'type: ', type(result))
        product_used = []
        for i in result:
            product = Product.objects.get(id=i)
            product_used.append(product)
        recipe_cooked = Recipe.objects.get(id=recipe_id)
        context = {"hello_dish": "Учет приготовленного блюда и использованных продуктов.", "form": form,
                   "result": result, "product_used": product_used, "recipe_cooked": recipe_cooked}
    else:
        context = {"hello_dish": "Учет приготовленного блюда и использованных продуктов.", "form": form}
    return render(request, "meal/dish_consumption.html", context)


def product_to_recipe(request):
    form = AddProductToRecipe()
    recipe_selected = request.GET.dict()
    print('recipe_selected: ', recipe_selected)
    print('пользователь: ', request.user)
    if recipe_selected:
        recipe_id = int(recipe_selected['recipe_id'])
        product_id = int(recipe_selected['product_id'])
        weight = int(recipe_selected['weight'])
        user = request.user
        user_id = user.id
        print('user_id: ', user_id, 'type: ', type(user_id))
        form_request = request.GET.dict()
        print('получено из формы: ', form_request)
        task = add_product_to_recipe.delay(recipe_id, product_id, weight, user_id)
        print('task: ', task)
        result = task.get()
        print('task.get(): ', result, 'type: ', type(result))
        recipe = Recipe.objects.get(id=recipe_id)
        product = Product.objects.get(id=product_id)
        weight = recipe.productinrecipe_set.get(product__id=product_id).weight_product
        print('weight: ', weight)
        context = {"hello_product": "Добавить продукт к рецепту или обновить вес продукта в рецепте.", "form": form,
                   "result": result, "product": product, "recipe": recipe, "weight": weight}
    else:
        context = {"hello_product": "Добавить продукт к рецепту или обновить вес продукта в рецепте.", "form": form}
    return render(request, "meal/product_to_recipe.html", context)


def recipe_analytic(request):
    form = ShowRecipesWithoutProduct()
    product_selected = request.GET.dict()
    print('product_selected: ', product_selected)
    if product_selected:
        product_id = int(product_selected['product_id'])
        print('product_id: ', product_id)
        product_selected_name = Product.objects.get(id=product_id)
        task = show_recipes_without_product.delay(product_id)
        print('task: ', task)
        result = task.get()
        print('task.get(): ', result, 'type: ', type(result))
        list_without = result['recipe_without_product_id']
        print('list_without: ', list_without)
        recipe_without_product = []
        for i in list_without:
            recipe_i = Recipe.objects.get(id=i)
            print('рецепт без продукта: ', recipe_i)
            recipe_without_product.append(recipe_i)
        list_with_low = result['recipe_with_low_product']
        recipe_with_low_product = []
        for i in list_with_low:
            recipe_i = Recipe.objects.get(id=i)
            recipe_with_low_product.append(recipe_i)
        context = {"hello_recipe_analytic": "Рецепты без продукта или с малым содержанием.",
                   "form": form, "result": result,
                   "recipe_without_product": recipe_without_product,
                   "recipe_with_low_product": recipe_with_low_product,
                   "product_selected_name": product_selected_name}
    else:
        context = {"hello_recipe_analytic": "Рецепты без продукта или с малым содержанием.", "form": form}
    return render(request, "meal/recipe_analytic.html", context)


def hello_name(request):
    print('request: ', request.GET)
    print('request.GET.dict(): ', request.GET.dict())
    name = [i for i in request.GET.values()]
    print('name: ', name, type(name))
    # print(int(name[1]))
    # print(int(request.GET['your_age']))
    context = {"hello_name": name}
    return render(request, "meal/hello_name.html", context)
