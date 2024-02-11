from django.db import models
from django.contrib.auth.models import User


class Dish(models.Model):
    """класс Блюдо, определяет код блюда, имя блюда."""
    name = models.CharField(max_length=64)

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return f'Dish name: {self.name}'


class Consumption(models.Model):
    """класс Расход Блюда, определяет количество приготовленных порций
    данного блюда."""
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    totalCooked = models.IntegerField(default=0)
    amountNewCooked = 1  # условие задания - количество новых порций = 1
    time_update = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def new_dish_cooked(self):
        self.totalCooked += self.amountNewCooked
        self.save()

    def __str__(self):
        return f'Dish cooked: {self.dish.name}, {self.totalCooked} servings.'


class Product(models.Model):
    """класс Продукты, определяет код, название продукта."""
    name = models.CharField(max_length=64)
    # dishWithProduct = models.ManyToManyField(Dish, through='Recipe')
    usedHowManyTimes = models.IntegerField(default=0)
    # dishes = models.ManyToManyField(Dish, through="Recipe")

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return f'Product name: {self.name}'


class Recipe(models.Model):
    """класс Рецепт Блюда, определяет код блюда, код продукта и вес
    этого продукта в блюде, краткую инструкцию по приготовлению"""
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, through='ProductInRecipe')
    # weight_product = models.IntegerField(default=0)
    summary = models.TextField(max_length=256, default=0)
    name = models.CharField(max_length=64, default=0)

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def add_product_to_recipe(self, recipe_id, product_id, weight):
        """Функция добавляет к указанному рецепту указанный продукт с указанным весом.
         Если в рецепте уже есть такой продукт, то функция должна поменять его вес
         в рецепте на указанный"""
        list_product = ProductInRecipe.objects.filter(recipe_id=recipe_id).all().values('product_id', flat=True)
        print('Набор словарей id продуктов в рецепте: ', list_product)
        list_product_id = [i for i in list_product]  # превращаем набор в список id продуктов в рецепте
        product_verified = Product.objects.get(id=product_id)
        if product_id not in list_product_id:
            print('Новый продукт в рецепте: ', product_verified.name)
            recipe_to_update = Recipe.objects.get(id=recipe_id)
            obj = ProductInRecipe(recipe=recipe_to_update, product=product_verified, weight_product=weight)
            obj.save()
            print('Новый продукт записан в рецепт')
        else:
            print('Уже есть такой продукт, обновляем вес: ')
            ProductInRecipe.objects.filter(recipe_id=recipe_id, product_id=product_id).update(weight_product=weight)
            print('Вес продукта обновлен')

    def show_recipes_without_product(self, product_id):
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

    def cook_recipe(self, recipe_id):
        """функция Блюдо приготовлено по рецепту recipe_id:
        увеличивает на единицу количество приготовленных блюд
        для каждого продукта, входящего в рецепт."""
        dish_cooked = Recipe.objects.get(id=recipe_id).dish
        print('приготовлено блюдо', dish_cooked.name, 'id блюда: ', dish_cooked.id)
        list_used_products = ProductInRecipe.objects.filter(recipe_id=recipe_id).values_list('product_id', flat=True)
        list_used_products_id = [i for i in list_used_products]
        print('список id использованных продуктов: ', list_used_products_id)
        for i in list_used_products_id:
            product = Product.objects.get(id=i)
            product.usedHowManyTimes += 1
            product.save()

    def __str__(self):
        return f'Recipe of {self.dish.name}'


class ProductInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    weight_product = models.IntegerField(default=0)

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return f'Product in recipe: {self.recipe.name} Product: {self.product.name} Weight: {self.weight_product}'
