from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Comment
from .forms import RecipeForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from notifications.models import Notification
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User


@login_required
def home(request):
    query = request.GET.get('q')
    if query:
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) |
            Q(ingredients__icontains=query)
        ).order_by('-created_at')
    else:
        recipes = Recipe.objects.all().order_by('-created_at')

    # 🔔 Get unread notifications for current user
    notifications = Notification.objects.filter(recipient=request.user, unread=True)

    return render(request, 'RecipeSharing/home.html', {
        'recipes': recipes,
        'notifications': notifications
    })

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('home')
    else:
        form = RecipeForm()
    return render(request, 'RecipeSharing/add_recipe.html', {'form': form})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'RecipeSharing/recipe_detail.html', {'recipe': recipe})

def register_view(request):
    success = False  # flag for success

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = RegisterForm()  # reset form after saving
    else:
        form = RegisterForm()

    return render(request, 'RecipeSharing/register.html', {
        'form': form,
        'success': success
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            # ✅ Don't redirect here — re-render the same page with the error
    return render(request, 'RecipeSharing/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_dashboard(request):
    user_recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    saved_recipes = Recipe.objects.filter(saved_by=request.user)
    context = {
        'recipes': user_recipes,
        'saved_recipes': saved_recipes,
    }
    return render(request, 'dashboard.html', context)

@login_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this recipe.")
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'RecipeSharing/edit_recipe.html', {'form': form})

@login_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this recipe.")
    if request.method == 'POST':
        recipe.delete()
        return redirect('dashboard')
    return render(request, 'RecipeSharing/confirm_delete.html', {'recipe': recipe})

@login_required
def like_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user in recipe.liked_by.all():
        recipe.liked_by.remove(request.user)
    else:
        recipe.liked_by.add(request.user)
    return redirect('home')

@login_required
def save_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.saved_by.filter(id=request.user.id).exists():
        recipe.saved_by.remove(request.user)
    else:
        recipe.saved_by.add(request.user)
    return redirect('home')

@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(recipe=recipe, author=request.user, content=content)
    return redirect('recipe_detail', pk=recipe_id)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Recipe, MealPlan

@login_required
def meal_plan(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meal_types = ['breakfast', 'lunch', 'dinner']
    recipes = Recipe.objects.all()

    if request.method == 'POST':
        # DELETE ALL old meal plans for this user
        MealPlan.objects.filter(user=request.user).delete()

        # Create new ones
        for day in days:
            for meal_type in meal_types:
                recipe_id = request.POST.get(f'{day}_{meal_type}')
                if recipe_id:
                    MealPlan.objects.create(
                        user=request.user,
                        day=day,
                        meal_type=meal_type,
                        recipe_id=recipe_id
                    )
        return redirect('view_meal_plan')

    return render(request, 'RecipeSharing/meal_plan.html', {
        'days': days,
        'meal_types': meal_types,
        'recipes': recipes
    })



@login_required
def add_meal(request):
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            form.save()
            return redirect('meal_plan')
    else:
        form = MealPlanForm()
    return render(request, 'RecipeSharing/add_meal.html', {'form': form})
@login_required
#def view_meal_plan(request):
 #   meal_plans = MealPlan.objects.filter(user=request.user)
  #  return render(request, 'RecipeSharing/view_meal_plan.html', {'meal_plans': meal_plans})


@login_required
def view_meal_plan(request):
    meal_plans = MealPlan.objects.filter(user=request.user)
    context = {'meal_plans': meal_plans}
    return render(request, 'RecipeSharing/view_meal_plan.html', context)


@login_required
def shopping_list_view(request):
    meals = MealPlan.objects.filter(user=request.user)
    ingredients = []

    for meal in meals:
        ingredients += [item.strip().capitalize() for item in meal.recipe.ingredients.split(',')]

    unique_ingredients = sorted(set(ingredients))
    return render(request, 'RecipeSharing/shopping_list.html', {'ingredients': unique_ingredients})

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        'user_count': User.objects.count(),
        'post_count': Recipe.objects.count(),
        'comment_count': Comment.objects.count(),
        'like_count': sum(recipe.liked_by.count() for recipe in Recipe.objects.all()),
        'saved_count': sum(recipe.saved_by.count() for recipe in Recipe.objects.all()),
        'posts': Recipe.objects.all(),
        'comments': Comment.objects.all(),
    }
    return render(request, 'RecipeSharing/admin_dashboard.html', context)


@user_passes_test(is_admin)
def delete_post(request, post_id):
    post = get_object_or_404(Recipe, id=post_id)
    post.delete()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect('admin_dashboard')
