from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.models import Profile

# Create your views here.

@login_required
def community_home(request):
    """View to show users with the same major as the logged-in user"""
    user_major = request.user.profile.major
    
    # Get users with the same major, excluding the current user
    if user_major:
        users_same_major = Profile.objects.filter(major=user_major).exclude(user=request.user)
    else:
        # If no major is selected, show users with no major selected
        users_same_major = Profile.objects.filter(major__isnull=True).exclude(user=request.user)

    context = {
        'users': users_same_major,
        'major_display': request.user.profile.get_major_display() if user_major else 'Unspecified',
        'major_value': user_major
    }
    
    return render(request, 'community/community_home.html', context)

@login_required
def user_profile(request, username):
    """View to show a specific user's profile"""
    user = get_object_or_404(User, username=username)
    
    context = {
        'profile_user': user,
    }
    
    return render(request, 'community/user_profile.html', context)
