from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import (
    Recipe,
    Rating,
    Comment,
    MealPlan,
    Meal,
    GroceryItem,
    CartItem,
    Notification
)


# ================= HOME =================

def home(request):

    recipes = Recipe.objects.all().order_by("-created_at")

    return render(
        request,
        "recipes/home.html",
        {
            "recipes": recipes
        }
    )



# ================= RECIPE =================


@login_required
def add_recipe(request):

    if request.method == "POST":

        recipe = Recipe.objects.create(

            title=request.POST["title"],

            ingredients=request.POST.get("ingredients"),

            instructions=request.POST["instructions"],

            category=request.POST["category"],

            calories=request.POST.get("calories",0),

            image=request.FILES.get("image"),

            user=request.user
        )


        return redirect(
            "recipe_detail",
            id=recipe.id
        )


    return render(
        request,
        "recipes/add_recipe.html"
    )




def recipe_detail(request,id):

    recipe = get_object_or_404(
        Recipe,
        id=id
    )


    comments = Comment.objects.filter(
        recipe=recipe
    )


    return render(
        request,
        "recipes/detail.html",
        {
            "recipe":recipe,
            "comments":comments
        }
    )




@login_required
def edit_recipe(request,id):

    recipe=get_object_or_404(
        Recipe,
        id=id,
        user=request.user
    )


    if request.method=="POST":

        recipe.title=request.POST["title"]

        recipe.ingredients=request.POST.get(
            "ingredients"
        )

        recipe.instructions=request.POST["instructions"]

        recipe.category=request.POST["category"]

        recipe.save()


        return redirect(
            "recipe_detail",
            id=id
        )


    return render(
        request,
        "recipes/edit.html",
        {
            "recipe":recipe
        }
    )




@login_required
def delete_recipe(request,id):

    recipe=get_object_or_404(
        Recipe,
        id=id,
        user=request.user
    )

    recipe.delete()

    return redirect("home")




# ================= LIKE =================


@login_required
def like_recipe(request,recipe_id):

    recipe=get_object_or_404(
        Recipe,
        id=recipe_id
    )


    if request.user in recipe.likes.all():

        recipe.likes.remove(request.user)

    else:

        recipe.likes.add(request.user)


    return redirect(
        "recipe_detail",
        id=recipe_id
    )




# ================= RATING =================


@login_required
def rate_recipe(request,recipe_id):

    recipe=get_object_or_404(
        Recipe,
        id=recipe_id
    )


    rating=int(
        request.POST.get("rating")
    )


    Rating.objects.update_or_create(

        user=request.user,

        recipe=recipe,

        defaults={
            "value":rating
        }

    )


    return redirect(
        "recipe_detail",
        id=recipe_id
    )




# ================= COMMENT =================


@login_required
def add_comment(request,recipe_id):

    recipe=get_object_or_404(
        Recipe,
        id=recipe_id
    )


    Comment.objects.create(

        user=request.user,

        recipe=recipe,

        text=request.POST["comment"]

    )


    return redirect(
        "recipe_detail",
        id=recipe_id
    )




# ================= PROFILE =================


@login_required
def profile(request):

    recipes=Recipe.objects.filter(
        user=request.user
    )


    return render(
        request,
        "recipes/profile.html",
        {
            "recipes":recipes
        }
    )




# ================= MEAL PLANNER =================

@login_required
def meal_planner(request):

    plans = MealPlan.objects.filter(
        user=request.user
    )


    plan_id = request.GET.get("plan_id")


    if plan_id:

        plan = get_object_or_404(
            MealPlan,
            id=plan_id,
            user=request.user
        )

    else:

        plan, created = MealPlan.objects.get_or_create(
            user=request.user,
            name="My Plan"
        )


    recipes = Recipe.objects.all()


    return render(
        request,
        "recipes/meal_planner.html",
        {
            "plan": plan,
            "plans": plans,
            "recipes": recipes,

            "days":[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ],

            "meal_types":[
                "Breakfast",
                "Lunch",
                "Dinner"
            ]
        }
    )
@login_required
def save_meal(request):

    recipe_id=request.POST.get("recipe")
    day=request.POST.get("day")
    meal_type=request.POST.get("meal_type")
    plan_id=request.POST.get("plan_id")


    plan=get_object_or_404(
        MealPlan,
        id=plan_id,
        user=request.user
    )


    recipe=get_object_or_404(
        Recipe,
        id=recipe_id
    )


    Meal.objects.update_or_create(

        user=request.user,

        plan=plan,

        day=day,

        meal_type=meal_type,

        defaults={
            "recipe":recipe
        }

    )


    # create grocery automatically

    GroceryItem.objects.filter(
        plan=plan
    ).delete()



    meals=Meal.objects.filter(
        plan=plan
    )


    for m in meals:

        for ing in m.recipe.ingredient_items.all():

            GroceryItem.objects.create(

                plan=plan,

                name=ing.name,

                quantity=ing.quantity,

                unit=ing.unit,

                price=ing.price

            )



    return JsonResponse({
        "status":"saved"
    })
@login_required
def get_meals(request):

    plan_id = request.GET.get("plan_id")

    meals=Meal.objects.filter(
        user=request.user,
        plan_id=plan_id
    )


    data=[]


    for meal in meals:

        data.append({

            "day":meal.day,

            "meal_type":meal.meal_type,

            "title":meal.recipe.title

        })


    return JsonResponse(
        data,
        safe=False
    )




@login_required
def delete_meal(request):

    Meal.objects.filter(
        id=request.POST["id"],
        user=request.user
    ).delete()


    return JsonResponse(
        {
            "status":"deleted"
        }
    )




@login_required
def clear_day(request):

    Meal.objects.filter(

        user=request.user,

        day=request.POST["day"]

    ).delete()


    return JsonResponse(
        {
            "status":"cleared"
        }
    )

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Recipe, Meal, MealPlan
@login_required
def auto_fill_meals(request):

    if request.method == "POST":

        plan_id = request.POST.get("plan_id")

        plan = get_object_or_404(
            MealPlan,
            id=plan_id,
            user=request.user
        )


        recipes = Recipe.objects.all()


        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]


        meal_types = [
            "Breakfast",
            "Lunch",
            "Dinner"
        ]


        # clear old data

        Meal.objects.filter(
            plan=plan,
            user=request.user
        ).delete()


        GroceryItem.objects.filter(
            plan=plan
        ).delete()



        index = 0


        for day in days:

            for meal_type in meal_types:


                recipe = recipes[index % recipes.count()]


                Meal.objects.create(

                    user=request.user,

                    plan=plan,

                    recipe=recipe,

                    day=day,

                    meal_type=meal_type

                )


                # ADD GROCERY HERE

                for ing in recipe.ingredient_items.all():

                    GroceryItem.objects.create(

                        plan=plan,

                        name=ing.name,

                        quantity=ing.quantity,

                        unit=ing.unit,

                        price=ing.price

                    )


                index += 1



        return JsonResponse({
            "status":"success"
        })


    return JsonResponse({
        "status":"error"
    })
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Meal, GroceryItem, CartItem


# ================= CALORIES DATA =================
@login_required
def calories_data(request):

    plan_id=request.GET.get("plan_id")


    meals=Meal.objects.filter(
        user=request.user,
        plan_id=plan_id
    )


    data={
        "Monday":0,
        "Tuesday":0,
        "Wednesday":0,
        "Thursday":0,
        "Friday":0,
        "Saturday":0,
        "Sunday":0
    }


    for m in meals:

        data[m.day]+=m.recipe.calories



    return JsonResponse(data)


# ================= GROCERY =================

@login_required
def grocery(request):

    plan_id=request.GET.get("plan_id")


    items=GroceryItem.objects.filter(
        plan_id=plan_id
    )


    result=[]

    total=0


    for i in items:

        price=i.quantity*i.price

        total+=price


        result.append({

            "name":i.name,

            "quantity":i.quantity,

            "unit":i.unit,

            "price":price

        })


    return JsonResponse({

        "all_items":result,

        "total_price":total

    })


# ================= CART =================

@login_required
def get_cart(request):

    items = CartItem.objects.filter(
        user=request.user
    )


    cart=[]


    for item in items:

        cart.append({

            "name":item.name,
            "quantity":item.quantity,
            "unit":item.unit,
            "price":item.price

        })


    return JsonResponse({

        "cart":cart

    })





@login_required
def grocery_list(request):

    plan=MealPlan.objects.get(
        user=request.user
    )


    items=GroceryItem.objects.filter(
        plan=plan
    )


    return JsonResponse(
        list(items.values()),
        safe=False
    )

@login_required
def add_to_cart(request):

    CartItem.objects.create(

        user=request.user,

        name=request.POST.get("name"),

        quantity=request.POST.get("quantity",1),

        unit=request.POST.get("unit","pcs"),

        price=request.POST.get("price",0)

    )


    return JsonResponse({
        "status":"added"
    })


# ================= FAVORITE =================


@login_required
def toggle_favorite(request,recipe_id):

    recipe=get_object_or_404(
        Recipe,
        id=recipe_id
    )


    if request.user in recipe.favorites.all():

        recipe.favorites.remove(
            request.user
        )

    else:

        recipe.favorites.add(
            request.user
        )


    return redirect(
        "recipe_detail",
        id=recipe_id
    )




# ================= NOTIFICATIONS =================


@login_required
def get_notifications(request):

    notifications=Notification.objects.filter(
        user=request.user
    )


    return JsonResponse(
        list(notifications.values()),
        safe=False
    )




# ================= DASHBOARD =================


@login_required
def dashboard(request):

    return render(
        request,
        "recipes/dashboard.html"
    )




# ================= AI =================


def ai_page(request):

    return render(
        request,
        "recipes/ai.html"
    )




def ai_recipe(request):

    return JsonResponse(
        {
            "recipe":"AI recipe generated"
        }
    )




def ai_suggestion(request):

    return JsonResponse(
        {
            "suggestion":"Try healthy food"
        }
    )




@login_required
def save_ai_recipe(request):

    return JsonResponse(
        {
            "status":"saved"
        }
    )




# ================= AUTH =================


def signup(request):

    if request.method=="POST":

        form=UserCreationForm(
            request.POST
        )


        if form.is_valid():

            user=form.save()

            login(
                request,
                user
            )

            return redirect(
                "home"
            )


    else:

        form=UserCreationForm()



    return render(
        request,
        "registration/signup.html",
        {
            "form":form
        }
    )




def logout_view(request):

    logout(request)

    return redirect(
        "home"
    )