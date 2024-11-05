from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100, unique=True, null=False)
    name = models.CharField(max_length=100, unique=True, null=False)
    email = models.EmailField(max_length=100, unique=True, null=False)
    password = models.CharField(max_length=100, null=False)
    favorite_cuisine = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    user_image=models.ImageField(upload_to='img/users/', null=True)

    def __str__(self):
        return self.username

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    instructions = models.TextField()
    recipe_image=models.ImageField(upload_to='img/recipe/', null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    food_type = models.CharField(max_length=20, null=True)  # e.g., Vegetarian or Non-Vegetarian
    time_taken = models.IntegerField(null=True) 
    style = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.title