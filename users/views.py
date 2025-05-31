from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('courses:course_list')

    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('courses:course_list')  # Добавить courses:
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
        'role': user.get_role_display()
    }
    return render(request, 'users/profile.html', context)

            
