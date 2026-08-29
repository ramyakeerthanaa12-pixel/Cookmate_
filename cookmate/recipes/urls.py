from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('ai/', views.ai_page, name='ai_page'),
    path('ai-recipe/', views.ai_recipe, name='ai_recipe'),
    path('add/', views.add_recipe, name='add_recipe'),

    path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),

    path('edit/<int:id>/', views.edit_recipe, name='edit_recipe'),

    path('delete/<int:id>/', views.delete_recipe, name='delete_recipe'),

    path('like/<int:recipe_id>/', views.like_recipe, name='like_recipe'),

    path('rate/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),

    path('comment/<int:recipe_id>/', views.add_comment, name='add_comment'),

    path('profile/', views.profile, name='profile'),

    path('meal-planner/', views.meal_planner, name='meal_planner'),

    path('save-meal/', views.save_meal, name='save_meal'),

    path('get-meals/', views.get_meals, name='get_meals'),

    path('delete-meal/', views.delete_meal, name='delete_meal'),

    path('clear-day/', views.clear_day, name='clear_day'),

    path('auto-fill/', views.auto_fill_meals, name='auto_fill_meals'),

    path('calories-data/', views.calories_data, name='calories_data'),

    path('grocery/', views.grocery, name='grocery'),

    path('grocery-list/', views.grocery_list, name='grocery_list'),

    path('cart/add/', views.add_to_cart, name='add_to_cart'),

    path('cart/get/', views.get_cart, name='get_cart'),

    path('favorite/<int:recipe_id>/', views.toggle_favorite, name='favorite'),

    path('notifications/', views.get_notifications, name='notifications'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('ai/', views.ai_page, name='ai_page'),

    path('ai/generate/', views.ai_recipe, name='ai_recipe'),

    path('ai/suggestion/', views.ai_suggestion, name='ai_suggestion'),

    path('ai/save/', views.save_ai_recipe, name='save_ai_recipe'),

    path('signup/', views.signup, name='signup'),

    path('logout/', views.logout_view, name='logout'),
]