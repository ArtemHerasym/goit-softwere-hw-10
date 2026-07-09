from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def signup_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:index")
    else:
        form = RegisterForm()

    return render(request, "users/signup.html", {"form": form})

def login_user(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user is not None:
            login(request, user)
            return redirect("quotes:index")

    return render(request, "users/login.html", {"form": AuthenticationForm()})

def logout_user(request):
    logout(request)
    return redirect("quotes:index")