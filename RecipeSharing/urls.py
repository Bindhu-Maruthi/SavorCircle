

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('recipe/<int:pk>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:pk>/delete/', views.delete_recipe, name='delete_recipe'),
    path('recipe/<int:recipe_id>/like/', views.like_recipe, name='like_recipe'),
    path('recipe/<int:recipe_id>/comment/', views.add_comment, name='add_comment'),
    path('recipe/<int:recipe_id>/save/', views.save_recipe, name='save_recipe'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('meal-plan/', views.meal_plan, name='meal_plan'),
    path('meal-plan/add/', views.add_meal, name='add_meal'),
    path('view-meal-plan/', views.view_meal_plan, name='view_meal_plan'),  # ✅ Add this line
    path('shopping-list/', views.shopping_list_view, name='shopping_list'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),

]

from django.shortcuts import render
from .models import Recipe

def home(request):
    recipes = Recipe.objects.all().order_by('-created_at')  # newest first
    return render(request, 'RecipeSharing/home.html', {'recipes': recipes})


