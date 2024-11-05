from django.contrib import admin
from django.urls import include, path
from.import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path("",views.index),
    path("loginpage/",views.login_btn),
    path("signuppage/",views.signup_btn),
    path('signup_user/', views.signup_user, name='signup_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('homepage/', views.homepage, name='homepage'),
    path('recipes/', views.recipes, name='recipes'),
    path('add_recipespage/', views.add_recipespage, name='add_recipespage'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('delete_recipe/<int:id>/', views.delete_recipe, name='delete_recipe'),
    path('edit_recipe/<int:id>/', views.edit_recipe, name='edit_recipe'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('recipe/', views.recipe, name='recipe'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('about/', views.about, name='about'),
    path('contactus/', views.contactus, name='contactus'),
    path('profile/', views.profile, name='profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)