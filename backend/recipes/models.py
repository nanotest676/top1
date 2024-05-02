from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator, RegexValidator

User = get_user_model()

class Ingredient(models.Model):
    title = models.CharField(
        "Название",
        max_length=200
    )
    unit = models.CharField(
        "Единица измерения",
        max_length=200
    )
    class Meta:
        verbose_name_plural = "Ингредиенты"
        ordering = ["title",]
        verbose_name = "Ингредиент"
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(
        "Название",
        max_length=200,
        unique=True
    )
    color = models.CharField(
        "Цвет",
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Значение не является HEX-цветом"
            )
        ],
        unique=True
    )
    slug = models.SlugField(
        "Уникальный слаг",
        unique=True,
        max_length=200
    )
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(
        "Название",
        max_length=200
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="recipes",
        null=True,
        on_delete=models.SET_NULL
    )
    description = models.TextField("Описание")
    image = models.ImageField(
        "Изображение",
        upload_to="recipes/"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[MinValueValidator(
            1, message="Минимальное значение должно быть не менее 1"
        )]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        related_name="recipes",
    )
    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"
    def __str__(self):
        return self.title

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name="shopping_recipes",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_recipes",
        verbose_name="Рецепт",
    )
    class Meta:
        verbose_name_plural = "Корзина покупок"
        verbose_name = "Корзина покупок"
        constraints = [
            UniqueConstraint(fields=["user", "recipe"], name="unique_shopping_cart")
        ]
    def __str__(self):
        return f"{self.user} добавил \"{self.recipe}\" в Корзину покупок"

class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            UniqueConstraint(fields=["user", "recipe"], name="unique_favourite")
        ]
    def __str__(self):
        return f"{self.user} добавил \"{self.recipe}\" в Избранное"

class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="ingredient_list",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[MinValueValidator(1, message="Минимальное количество 1!")]
    )
    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
    def __str__(self):
        return f"{self.ingredient.title} ({self.ingredient.unit}) - {self.amount}"
