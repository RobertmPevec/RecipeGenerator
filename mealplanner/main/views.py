from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from openai import OpenAI
import logging
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages

# Initialize OpenAI client
client = OpenAI(api_key="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")

# Logger setup
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'main/home.html')

class CustomLoginView(auth_views.LoginView):
    template_name = "main/login.html"

def redirect_to_login(request):
    return redirect('login')

def logout_user(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    if request.method == 'POST':
        # Extract form data
        ingredients = request.POST.get('ingredients', '').strip()
        meal_type = request.POST.get('meal-type', '').strip()
        dietary_choice = request.POST.get('dietary-choice', '').strip()
        meal_count = request.POST.get('meal-count', '').strip()
        calories = request.POST.get('calories', '').strip()
        protein = request.POST.get('protein', '').strip()

        try:
            # Convert optional fields to integers
            meal_count = int(meal_count) if meal_count else None
            calories = int(calories) if calories else None
            protein = int(protein) if protein else None

            # Generate a prompt and query the API
            prompt = f"""
            Please generate {meal_count if meal_count else 'a'} meal(s) using these ingredients: {ingredients}. 
            This is for a {meal_type} meal that follows a {dietary_choice} diet. 
            Also include a link to a simular recipe online with an image to what the recipe will look close to
            Finally end off with a simple enjoy message and nothing else.
            """

            if calories:
                prompt += f"The total calories should not exceed {calories} calories. "

            if protein:
                prompt += f"The meal(s) should contain around {protein}g of protein. "

            prompt += "If the inputs are unrealistic, generate a practical meal using the provided information."

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            recipe = response.choices[0].message.content.strip()

            return JsonResponse({
                'success': True,
                'received_data': {
                    'ingredients': ingredients,
                    'meal_type': meal_type,
                    'dietary_choice': dietary_choice,
                    'meal_count': meal_count,
                    'calories': calories,
                    'protein': protein,
                },
                'recipe': recipe
            })

        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'main/dashboard.html')

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        messages.success(request, 'Thank you for reaching out! We will get back to you soon.')
        return redirect('contact')
    return render(request, 'main/contact.html')

def login_register_view(request):
    # Ensure no "None" value is passed to the username field
    login_form = AuthenticationForm(request=request, data=request.POST or None)
    if request.method == "POST" and "login_submit" in request.POST:
        # Overwrite `username` in the POST data if `None` is present
        login_form.data = login_form.data.copy()
        login_form.data["username"] = login_form.data.get("username") or ""

    register_form = UserCreationForm(request.POST or None)

    if request.method == "POST":
        if "login_submit" in request.POST and login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect("dashboard")
        elif "register_submit" in request.POST and register_form.is_valid():
            register_form.save()
            messages.success(request, "Your account has been created successfully! Please log in.")
            return redirect("login")

    return render(request, "main/login.html", {
        "login_form": login_form,
        "register_form": register_form,
    })
