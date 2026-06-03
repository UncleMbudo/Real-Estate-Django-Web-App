from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from contacts.models import Contact
from listings.models import Favourite


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username, password=password,
            email=email, first_name=first_name, last_name=last_name
        )
        user.save()
        messages.success(request, 'Account created! You can now log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def dashboard(request):
    contacts = Contact.objects.filter(user=request.user).order_by('-contact_date')
    favourites = Favourite.objects.filter(user=request.user).select_related('listing')
    return render(request, 'accounts/dashboard.html', {
        'contacts': contacts,
        'favourites': favourites,
    })
