from celery import shared_task

from meal.models import *

@shared_task
def add_product_to_recipe(recipe_id, product_id, weight, user_id):
    """Функция добавляет к указанному рецепту указанный продукт с указанным весом.
     Если в рецепте уже есть такой продукт, то функция должна поменять его вес
     в рецепте на указанный"""
    list_product = ProductInRecipe.objects.filter(recipe_id=recipe_id).all().values('product_id')
    print('Набор словарей id продуктов в рецепте: ', list_product)
    list_product_id = [int(i['product_id']) for i in list_product]  # превращаем набор в список id продуктов в рецепте
    print('Список id продуктов в рецепте list_product_id: ', list_product_id)
    product_verified = Product.objects.get(id=product_id)

    if product_id in list_product_id:
        print('Уже есть такой продукт, обновляем вес: ')
        ProductInRecipe.objects.filter(recipe_id=recipe_id, product_id=product_id).update(weight_product=weight)
        print('Вес продукта обновлен')
        return 'Вес продукта обновлен'
    else:
        print('Новый продукт в рецепте: ', product_verified.name)
        recipe_to_update = Recipe.objects.get(id=recipe_id)
        obj = ProductInRecipe(recipe=recipe_to_update, product=product_verified, weight_product=weight, user=user_id)
        obj.save()
        print(f'Новый продукт добавлен пользователем {user_id} в рецепт')
        return 'Новый продукт добавлен в рецепт'

@shared_task
def show_recipes_without_product(product_id):
    """Функция возвращает HTML страницу, на которой размещена таблица. В таблице
    отображены id и названия всех рецептов, в которых указанный продукт отсутствует или
    присутствует в количестве меньше 10 грамм. Страница должна генерироваться с использованием
    Django templates."""
    recipe_without_product = Recipe.objects.all().exclude(product__id=product_id).values_list('id', flat=True)
    # преобразуем Queryset в список id
    recipe_without_product_id = [i for i in recipe_without_product]

    # из другой модели получаем Queryset с набором объектов только с одним искомым продуктом
    recipe_with_product = ProductInRecipe.objects.filter(product_id=product_id)
    # отфильтровываем по весу и получаем Queryset со списком id рецептов
    filtered_weight = recipe_with_product.filter(weight_product__lt=10).values_list('recipe_id', flat=True)
    # преобразуем в список id
    recipe_with_low_product_id = [i for i in filtered_weight]
    print('filtered_weight: ', filtered_weight, ' list: ', [i for i in filtered_weight])
    context = {"recipe_without_product_id": recipe_without_product_id,
               "recipe_with_low_product": recipe_with_low_product_id}
    print('recipe_without_product_id: ', recipe_without_product_id,
          ' recipe_with_low_product_id: ', recipe_with_low_product_id)
    return context

@shared_task
def cook_recipe(recipe_id):
    """функция Блюдо приготовлено по рецепту recipe_id:
    увеличивает на единицу количество приготовленных блюд
    для каждого продукта, входящего в рецепт."""
    dish_cooked = Recipe.objects.get(id=recipe_id).dish
    print('приготовлено блюдо', dish_cooked.name, 'id блюда: ', dish_cooked.id)
    list_used_products = ProductInRecipe.objects.filter(recipe_id=recipe_id).values_list('product_id', flat=True)
    print('list_used_products: ', list_used_products)
    list_used_products_id = [int(i) for i in list_used_products]
    print('список id использованных продуктов: ', list_used_products_id)
    for i in list_used_products_id:
        product = Product.objects.get(id=i)
        product.usedHowManyTimes += 1
        product.save()
    context = list_used_products_id
    return context
