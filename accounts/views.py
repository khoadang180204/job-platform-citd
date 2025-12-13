from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import UserProfile
from jobs.models import Company

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on role
            if hasattr(user, 'profile') and user.profile.is_employer():
                return redirect('dashboard:index')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    """User registration with role selection"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', '').lower()  # Get and lowercase role
        
        # Validate role
        if role not in ['candidate', 'employer']:
            messages.error(request, 'Please select a valid account type!')
            return render(request, 'accounts/register.html')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/register.html', {
                'form_data': {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'role': role
                }
            })
        
        # Check username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'accounts/register.html', {
                'form_data': {
                    'email': email,
                    'first_name': first_name,
                    'role': role
                }
            })
        
        # Check email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'accounts/register.html', {
                'form_data': {
                    'username': username,
                    'first_name': first_name,
                    'role': role
                }
            })
        
        # Create user with transaction
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name
                )
                
                # Create profile with role
                profile = UserProfile.objects.create(
                    user=user,
                    role=role
                )
                
                # If employer, create company profile
                if role == 'employer':
                    Company.objects.create(
                        user=user,
                        name=first_name or username
                    )
                    messages.success(request, f'Welcome {first_name}! Your employer account is ready. Please login to access your dashboard.')
                else:
                    messages.success(request, f'Welcome {first_name}! Your candidate account is ready. Please login to browse jobs.')
                
                return redirect('accounts:login')
        
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')

def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required(login_url='accounts:login')
def profile_view(request):
    """User profile view"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', profile.bio)
        profile.phone = request.POST.get('phone', profile.phone)
        
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
    
    context = {
        'profile': profile,
    }
    
    # If employer, add company info
    if profile.is_employer() and hasattr(request.user, 'company'):
        context['company'] = request.user.company
    
    return render(request, 'accounts/profile.html', context)

@login_required(login_url='accounts:login')
def saved_jobs_view(request):
    """Candidate view saved jobs"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_candidate():
        messages.error(request, 'Only candidates can save jobs!')
        return redirect('home')
    
    # TODO: Implement saved jobs (thêm SavedJob model nếu cần)
    # Hiện tại redirect về jobs list
    return redirect('jobs:list')

@login_required(login_url='accounts:login')
def my_applications_view(request):
    """Candidate view their applications"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_candidate():
        messages.error(request, 'Only candidates can view applications!')
        return redirect('home')
    
    from jobs.models import Application
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'applications': applications
    }
    
    return render(request, 'accounts/my_applications.html', context)