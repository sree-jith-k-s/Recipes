import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import *
from .models import *

# Create your views here.
def index(request):
    recipes = Recipe.objects.all().order_by('-created_at')[:3]
    recipes_with_time = []
    for recipe in recipes:
        time_taken = recipe.time_taken

        # Only calculate hours and minutes if time_taken is not None
        if time_taken is not None:
            if time_taken > 59:
                hours = time_taken // 60
                time=60*hours
                minutes = time_taken - time
            else:
                hours = 0
                minutes = time_taken
        else:
            hours = 0
            minutes = 0  # Default to 0 if time_taken is None

        # Append a dictionary with the recipe and calculated time
        recipes_with_time.append({
            'recipe': recipe,
            'hours': hours,
            'minutes': minutes
        })
    return render(request, 'index.html',{'recipes_with_time':recipes_with_time})
def login_btn(request):
    return render(request,"login.html")
def signup_btn(request):
    return render(request,"signup.html")
def signup_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        favorite_cuisine = request.POST.get('favorite_cuisine')
        photo = request.FILES.get('photo')
        
        # Basic validation checks
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html')

        # Save the user
        user = User(
            username=username,
            name=name,
            email=email,
            password=make_password(password),  # Hash the password
            favorite_cuisine=favorite_cuisine,
            user_image=photo
        )
        if photo:
                # Save the uploaded photo to the FileSystemStorage
                fs = FileSystemStorage(location=os.path.join('static', 'img', 'user'))
                file = fs.save(photo.name, photo)  # Save the file with its name
                user.photo = fs.url(file)  # Store the URL in the Recipe instance
            
        user.save()
        
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('/loginpage/')  # Replace 'login' with the URL name of your login page

def login_user(request):
    if request.method == 'POST':
        # Get username/email and password from the form
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Check if the user exists by username or email
        try:
            user = User.objects.get(username=username_or_email)  # First check username
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)  # Then check email
            except User.DoesNotExist:
                # If username or email does not match, show an alert
                return HttpResponse(
                    "<script>alert('Invalid username or email.');"
                    "window.location.href='/loginpage';</script>"
                )

        # Verify the password
        if user and check_password(password, user.password):  # Check hashed password
            # Log the user in
            request.session['user_id'] = user.id  # Save user ID in session
            return redirect('/homepage/')  # Redirect to the home page or dashboard
        else:
            # If the password is incorrect, show an alert
            return HttpResponse(
                "<script>alert('Invalid password.');"
                "window.location.href='/loginpage';</script>"
            )

    return redirect('/loginpage')
def homepage(request):
    user_id = request.session.get('user_id')
    user = None
    recipes = Recipe.objects.all().order_by('-created_at')[:3]
    if user_id:
        user = User.objects.get(id=user_id)
    recipes_with_time = []
    for recipe in recipes:
        time_taken = recipe.time_taken

        # Only calculate hours and minutes if time_taken is not None
        if time_taken is not None:
            if time_taken > 59:
                hours = time_taken // 60
                time=60*hours
                minutes = time_taken - time
            else:
                hours = 0
                minutes = time_taken
        else:
            hours = 0
            minutes = 0  # Default to 0 if time_taken is None

        # Append a dictionary with the recipe and calculated time
        recipes_with_time.append({
            'recipe': recipe,
            'hours': hours,
            'minutes': minutes
        })

    return render(request,'homepage.html',{'user': user,'recipes_with_time':recipes_with_time})
def recipes(request):
    user_id = request.session.get('user_id')  # Get user ID from session
    user = None
    recipes = Recipe.objects.all()  # Get all recipes by default

    # Check if user ID is in session
    if user_id:  
        user = get_object_or_404(User, id=user_id)  # Retrieve the user

    # Get the search query from the GET request
    search_query = request.GET.get('q', '')
    
    # Filter recipes if a search query is provided
    if search_query:
        recipes = recipes.filter(title__icontains=search_query) | recipes.filter(ingredients__icontains=search_query)

    # Prepare a list to hold recipes with calculated time
    recipes_with_time = []
    for recipe in recipes:
        time_taken = recipe.time_taken

        # Only calculate hours and minutes if time_taken is not None
        if time_taken is not None:
            if time_taken > 59:
                hours = time_taken // 60
                time=60*hours
                minutes = time_taken - time
            else:
                hours = 0
                minutes = time_taken
        else:
            hours = 0
            minutes = 0  # Default to 0 if time_taken is None

        # Append a dictionary with the recipe and calculated time
        recipes_with_time.append({
            'recipe': recipe,
            'hours': hours,
            'minutes': minutes
        })

    return render(request, 'Recipes.html', {'user': user, 'recipes_with_time': recipes_with_time, 'search_query': search_query})
def add_recipespage(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = User.objects.get(id=user_id)

    return render(request,'add_recipes.html',{'user': user})
def add_recipe(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        food_type = request.POST.get('food_type')
        time_taken = request.POST.get('time_taken')
        style = request.POST.get('style')
        
        # Safely get the uploaded file
        photo = request.FILES.get('photo')
        user_id = request.session.get('user_id')

        # Ensure user_id is valid and user exists
        if user_id:
            user = User.objects.get(id=user_id)

            # Create a new Recipe instance
            recipe = Recipe(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                food_type=food_type,
                time_taken=time_taken,
                created_by=user,
                recipe_image=photo,
                style=style
            )

            # Handle the photo if it exists
            if photo:
                # Save the uploaded photo to the FileSystemStorage
                fs = FileSystemStorage(location=os.path.join('static', 'img', 'recipe'))
                file = fs.save(photo.name, photo)  # Save the file with its name
                recipe.photo = fs.url(file)  # Store the URL in the Recipe instance
            
            # Save the recipe instance to the database
            recipe.save()  
            return redirect('/recipes')
        else:
            # Handle case where user_id is not found
            return redirect('/add_recipespage')  # Redirect to login or appropriate page

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    time_taken = recipe.time_taken

        # Only calculate hours and minutes if time_taken is not None
    if time_taken is not None:
        if time_taken > 59:
            hours = time_taken // 60
            time=60*hours
            minutes = time_taken - time
        else:
            hours = 0
            minutes = time_taken
    else:
        hours = 0
        minutes = 0  # Default to 0 if time_taken is None
    context = {
        'recipe': recipe,
        'hours': hours,
        'minutes': minutes
    }
    return render(request, 'recipe_details.html', context)
def my_recipes(request):
    user_id = request.session.get('user_id')
    recipes = []  # Initialize recipes as an empty list
    
    if user_id:
        user = get_object_or_404(User, id=user_id)  # Get the user safely
        recipes = user.recipes.all()  # Retrieve all recipes for the logged-in user

    return render(request, 'my_recipes.html', {'user': user, 'recipes': recipes})
def logout_user(request):
    # Clear the session data, effectively logging out the user
    request.session.flush()  # Clears all session data

    # Optionally, you can display a logout message
    messages.success(request, "Logged out successfully!")

    # Redirect the user to the login page or homepage
    return redirect('/loginpage/')
 # Ensure that the user is logged in before allowing deletion
def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)  # Retrieve the recipe by ID
    if request.method == 'POST':
        recipe.delete()  # Delete the recipe instance
        # Optionally, you can add a success message here
        return redirect('/my_recipes')  # Redirect to the page listing recipes
    return redirect('/my_recipes') 
def edit_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)  # Get the recipe by ID

    if request.method == 'POST':
        # Update the recipe with new data
        recipe.title = request.POST.get('title')
        recipe.ingredients = request.POST.get('ingredients')
        recipe.instructions = request.POST.get('instructions')
        recipe.save()  # Save the updated recipe

        return redirect('my_recipes')  # Redirect to a list of recipes or another appropriate page

    return render(request, 'edit_recipe.html', {'recipe': recipe})

def about(request):
    return render(request,"aboutus.html")
def aboutus(request):
    return render(request,"about.html")
def contact(request):
    return render(request,"contact.html")
def contactus(request):
    return render(request,"contactus.html")
def blog(request):
    return render(request,"blog.html")
def recipe(request):
    recipes = Recipe.objects.all()  # Get all recipes by default

    # Get the search query from the GET request
    search_query = request.GET.get('q', '')
    
    # Filter recipes if a search query is provided
    if search_query:
        recipes = recipes.filter(title__icontains=search_query) | recipes.filter(ingredients__icontains=search_query)

    # Prepare a list to hold recipes with calculated time
    recipes_with_time = []
    for recipe in recipes:
        time_taken = recipe.time_taken

        # Only calculate hours and minutes if time_taken is not None
        if time_taken is not None:
            if time_taken > 59:
                hours = time_taken // 60
                time=60*hours
                minutes = time_taken - time
            else:
                hours = 0
                minutes = time_taken
        else:
            hours = 0
            minutes = 0  # Default to 0 if time_taken is None

        # Append a dictionary with the recipe and calculated time
        recipes_with_time.append({
            'recipe': recipe,
            'hours': hours,
            'minutes': minutes
        })

    return render(request, 'Recipe.html', {'recipes_with_time': recipes_with_time, 'search_query': search_query})
def profile(request):
    user_id = request.session.get('user_id')
    recipes = Recipe.objects.filter(created_by=user_id)
    recipes_count = recipes.count()
    
    if user_id:
        user = get_object_or_404(User, id=user_id)  # Get the user safely

    return render(request, 'profile.html', {'user': user,'recipes_count': recipes_count})