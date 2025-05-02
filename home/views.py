from django.shortcuts import render
from django.contrib.auth.models import User
from tasks.models import Task
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.db import DatabaseError

def home(request):
    try:
        # User statistics
        total_users = User.objects.count()
        
        # Task statistics - only shown if user is authenticated
        task_stats = None
        mentor_tasks = []
        productivity_score = 0
        
        if request.user.is_authenticated:
            # Get task statistics for the current user
            total_tasks = Task.objects.filter(user=request.user).count()
            completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
            overdue_tasks = Task.objects.filter(
                user=request.user, 
                completed=False,
                due_date__lt=timezone.now()
            ).count()
            
            # Calculate completion rate
            completion_rate = 0
            if total_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100
                
            # Calculate productivity score (0-100)
            if total_tasks > 0:
                # Base score is completion rate
                productivity_score = completion_rate
                
                # Penalty for overdue tasks (up to -20 points)
                overdue_penalty = min(20, (overdue_tasks / max(1, total_tasks)) * 40)
                productivity_score -= overdue_penalty
                
                # Bonus for recent activity (up to +10 points)
                recent_tasks = Task.objects.filter(
                    user=request.user,
                    created_date__gte=timezone.now() - timedelta(days=7)
                ).count()
                activity_bonus = min(10, (recent_tasks / max(1, total_tasks)) * 20)
                productivity_score += activity_bonus
                
                # Ensure score is within 0-100 range
                productivity_score = max(0, min(100, productivity_score))
            
            # High priority tasks that aren't completed (mentor suggestions)
            mentor_tasks = Task.objects.filter(
                user=request.user,
                priority='high',
                completed=False
            ).order_by('due_date')[:3]
            
            # Package all stats
            task_stats = {
                'total': total_tasks,
                'completed': completed_tasks,
                'overdue': overdue_tasks,
                'completion_rate': int(completion_rate),
                'productivity_score': int(productivity_score),
            }
        
        # Tips for improving productivity
        productivity_tips = [
            "Break large tasks into smaller, manageable chunks",
            "Set specific deadlines for all your tasks",
            "Focus on high-priority tasks first",
            "Take short breaks between work sessions",
            "Review and plan your tasks at the beginning of each day",
            "Minimize distractions during focused work time",
            "Celebrate your achievements, even small ones",
            "Use the calendar view to visualize your weekly schedule"
        ]
        
        # Achievements
        achievements = []
        if request.user.is_authenticated:
            if completed_tasks >= 5:
                achievements.append({
                    'title': 'Getting Started',
                    'description': 'Complete 5 tasks',
                    'icon': 'star',
                    'unlocked': True
                })
            else:
                achievements.append({
                    'title': 'Getting Started',
                    'description': 'Complete 5 tasks',
                    'icon': 'star',
                    'unlocked': False,
                    'progress': completed_tasks * 20
                })
                
            if completed_tasks >= 20:
                achievements.append({
                    'title': 'Productivity Master',
                    'description': 'Complete 20 tasks',
                    'icon': 'trophy',
                    'unlocked': True
                })
            else:
                achievements.append({
                    'title': 'Productivity Master',
                    'description': 'Complete 20 tasks',
                    'icon': 'trophy',
                    'unlocked': False,
                    'progress': min(100, completed_tasks * 5)
                })
                
            # High priority achievement
            high_priority_completed = Task.objects.filter(
                user=request.user,
                priority='high',
                completed=True
            ).count()
            
            if high_priority_completed >= 10:
                achievements.append({
                    'title': 'Priority Focused',
                    'description': 'Complete 10 high-priority tasks',
                    'icon': 'fire',
                    'unlocked': True
                })
            else:
                achievements.append({
                    'title': 'Priority Focused',
                    'description': 'Complete 10 high-priority tasks',
                    'icon': 'fire',
                    'unlocked': False,
                    'progress': min(100, high_priority_completed * 10)
                })
        
        context = {
            'total_users': total_users,
            'task_stats': task_stats,
            'mentor_tasks': mentor_tasks,
            'productivity_tips': productivity_tips,
            'achievements': achievements,
        }
        
    except DatabaseError:
        # If database is not ready, show minimal context
        context = {
            'total_users': 0,
            'task_stats': None,
            'mentor_tasks': [],
            'productivity_tips': productivity_tips,
            'achievements': [],
            'database_error': True
        }
    
    return render(request, 'home/home.html', context)
