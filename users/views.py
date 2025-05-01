from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F, ExpressionWrapper, fields, Q
import random

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, 
                                   instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)

@login_required
def settings(request):
    """View for user settings including password change and theme selection"""
    return render(request, 'users/settings.html')

def prizes(request):
    """View for the prize system page showing top users and subscription information"""
    # In a real implementation, you would actually calculate the top user based on task metrics
    # For now, we'll simulate a fixed "top user" rather than randomly selecting one
    
    try:
        # Get the first user as our consistent top user
        # In a real implementation, this would be based on task metrics using:
        # User.objects.annotate(
        #    completed_tasks=Count('task', filter=Q(task__completed=True))
        # ).order_by('-completed_tasks').first()
        top_user = User.objects.first()
        
        # Fixed stats for the top user
        top_user_stats = {
            'tasks_completed': 342,
            'hours_spent': 287,
            'completion_rate': 98,
            'prize_amount': "1,240"
        }
        
        # For logged-in users, show their rank
        user_rank = None
        user_progress = None
        if request.user.is_authenticated:
            # In a real implementation, this would be calculated based on their position
            # relative to other users and the top user
            if request.user == top_user:
                user_rank = 1
                user_progress = 100
            else:
                user_rank = random.randint(5, 50)
                user_progress = random.randint(20, 80)
            
    except Exception:
        # Fallback to None if there are no users or other errors
        top_user = None
        top_user_stats = None
    
    context = {
        'top_user': top_user,
        'top_user_stats': top_user_stats,
        'user_rank': user_rank,
        'user_progress': user_progress
    }
    
    return render(request, 'users/prizes.html', context)
