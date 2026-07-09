from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegisterForm


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
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("quotes:index")

    return render(request, "users/login.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("quotes:index")
