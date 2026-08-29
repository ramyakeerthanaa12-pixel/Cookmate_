from django.db import models
from django.contrib.auth.models import User


# ================= RECIPE =================
class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ("Veg", "Veg"),
        ("Non-Veg", "Non-Veg"),
        ("Dessert", "Dessert"),
        ("Snack", "Snack"),
    ]

    title = models.CharField(max_length=200)

    # Backward compatibility
    ingredients = models.TextField(blank=True, null=True)

    instructions = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)

    calories = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name='liked_recipes', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)

    def avg_rating(self):
        return self.rating_set.aggregate(models.Avg('value'))['value__avg'] or 0

    def total_likes(self):
        return self.likes.count()

    def total_favorites(self):
        return self.favorites.count()

    def __str__(self):
        return self.title


# ================= INGREDIENT =================
class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredient_items",
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20)
    price = models.FloatField(default=0)   # price per unit

    def total_price(self):
        return self.quantity * self.price   # ✅ FIXED

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.unit})"

# ================= RATING =================
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    value = models.IntegerField()

    class Meta:
        unique_together = ('user', 'recipe')

    def save(self, *args, **kwargs):
        # Clamp rating between 1–5
        self.value = max(1, min(5, self.value))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.recipe.title} - {self.value}"


# ================= COMMENT =================
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}"


# ================= MEAL PLAN =================
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_meals(self):
        return self.meal_set.count()

    def __str__(self):
        return f"{self.user.username} - {self.name}"


# ================= MEAL =================
class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="meals"
    )

    day = models.CharField(max_length=20)

    meal_type = models.CharField(
        max_length=20,
        choices=[
            ("Breakfast", "Breakfast"),
            ("Lunch", "Lunch"),
            ("Dinner", "Dinner"),
        ],
        default="Breakfast"
    )

    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'day', 'meal_type', 'plan')

    def __str__(self):
        return f"{self.plan.name} - {self.day} ({self.meal_type})"


# ================= GROCERY =================
class GroceryItem(models.Model):
    plan = models.ForeignKey(
        MealPlan,
        on_delete=models.CASCADE,
        related_name="grocery_items"
    )

    name = models.CharField(max_length=200)
    quantity = models.FloatField(default=1)
    unit = models.CharField(max_length=20, default="pcs")
    price = models.FloatField(default=0)

    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.unit})"


# ================= NOTIFICATION =================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"


# ================= CART =================
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField(default=1)
    unit = models.CharField(max_length=20, default="unit")  # ✅ added default
    price = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.unit})"

# ================= USER PREFERENCES =================
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    daily_calorie_goal = models.IntegerField(default=2000)

    def __str__(self):
        return self.user.username