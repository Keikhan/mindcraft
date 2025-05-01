from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from django.utils import timezone
import calendar
from datetime import datetime, timedelta
from calendar import monthrange
import json
from django.db.models import Count, Q

@login_required
def dashboard(request):
    # Get current month and year or from request parameters
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Create date object for the requested month
    current_date = datetime(year, month, 1)
    
    # Get next and previous month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Get calendar data for the month
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get tasks for the current user for this month
    month_start = datetime(year, month, 1)
    if month == 12:
        next_month_date = datetime(year + 1, 1, 1)
    else:
        next_month_date = datetime(year, month + 1, 1)
    
    month_tasks = Task.objects.filter(
        user=request.user,
        due_date__gte=month_start,
        due_date__lt=next_month_date
    )
    
    # Create a calendar with tasks
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': '', 'tasks': []})
            else:
                day_tasks = [task for task in month_tasks if task.due_date and task.due_date.day == day]
                week_data.append({'day': day, 'tasks': day_tasks})
        calendar_data.append(week_data)
    
    # Get upcoming tasks (next 7 days)
    today = timezone.now().date()
    upcoming_date = today + timedelta(days=7)
    upcoming_tasks = Task.objects.filter(
        user=request.user,
        completed=False,
        due_date__date__gte=today,
        due_date__date__lte=upcoming_date
    ).order_by('due_date')
    
    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        user=request.user,
        completed=False,
        due_date__date__lt=today
    ).order_by('due_date')
    
    # Get all tasks for the comprehensive list
    all_tasks = Task.objects.filter(
        user=request.user
    ).order_by('completed', 'due_date')
    
    context = {
        'calendar_data': calendar_data,
        'month': month_name,
        'year': year,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        'all_tasks': all_tasks,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'current_month': now.month,
        'current_year': now.year,
    }
    
    return render(request, 'tasks/dashboard.html', context)

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Update Task'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def analytics(request):
    """View for showing task analytics and progress charts"""
    # Get the selected time period from the request (default to 'week')
    period = request.GET.get('period', 'week')
    
    # Get current date for reference
    today = timezone.now().date()
    
    # Initialize data dictionaries for the charts
    labels = []
    completion_data = []
    creation_data = []
    overdue_data = []
    
    # Calculate date ranges based on selected period
    if period == 'day':
        # Last 24 hours broken down by hours
        start_date = timezone.now() - timedelta(days=1)
        
        # Create hourly buckets
        for hour in range(24):
            hour_start = timezone.now() - timedelta(hours=24-hour)
            hour_end = timezone.now() - timedelta(hours=23-hour)
            
            # Format label as hour (e.g., "2 PM")
            labels.append(hour_start.strftime("%I %p"))
            
            # Count tasks completed in this hour
            completed_count = Task.objects.filter(
                user=request.user,
                completed=True,
                due_date__gte=hour_start,
                due_date__lt=hour_end
            ).count()
            
            # Count tasks created in this hour
            created_count = Task.objects.filter(
                user=request.user,
                created_date__gte=hour_start,
                created_date__lt=hour_end
            ).count()
            
            # Count overdue tasks in this hour
            overdue_count = Task.objects.filter(
                user=request.user,
                completed=False,
                due_date__lt=hour_end,
                due_date__gte=hour_start
            ).count()
            
            completion_data.append(completed_count)
            creation_data.append(created_count)
            overdue_data.append(overdue_count)
            
    elif period == 'week':
        # Last 7 days
        for day in range(7):
            day_date = today - timedelta(days=6-day)
            labels.append(day_date.strftime("%a"))  # Day abbreviation (Mon, Tue, etc.)
            
            # Count tasks completed on this day
            completed_count = Task.objects.filter(
                user=request.user,
                completed=True,
                due_date__date=day_date
            ).count()
            
            # Count tasks created on this day
            created_count = Task.objects.filter(
                user=request.user,
                created_date__date=day_date
            ).count()
            
            # Count overdue tasks on this day
            overdue_count = Task.objects.filter(
                user=request.user,
                completed=False,
                due_date__date__lt=day_date
            ).count()
            
            completion_data.append(completed_count)
            creation_data.append(created_count)
            overdue_data.append(overdue_count)
            
    elif period == 'month':
        # Current month by day
        current_month = today.month
        current_year = today.year
        days_in_month = monthrange(current_year, current_month)[1]
        
        for day in range(1, days_in_month + 1):
            day_date = datetime(current_year, current_month, day).date()
            
            # Skip future days
            if day_date > today:
                continue
                
            labels.append(day)  # Just the day number
            
            # Count tasks completed on this day
            completed_count = Task.objects.filter(
                user=request.user,
                completed=True,
                due_date__date=day_date
            ).count()
            
            # Count tasks created on this day
            created_count = Task.objects.filter(
                user=request.user,
                created_date__date=day_date
            ).count()
            
            # Count overdue tasks on this day
            overdue_count = Task.objects.filter(
                user=request.user,
                completed=False,
                due_date__date__lt=day_date
            ).count()
            
            completion_data.append(completed_count)
            creation_data.append(created_count)
            overdue_data.append(overdue_count)
    
    # Get completion rate for different time periods
    all_tasks_count = Task.objects.filter(user=request.user).count()
    completed_tasks_count = Task.objects.filter(user=request.user, completed=True).count()
    
    # Tasks due this week
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_tasks = Task.objects.filter(
        user=request.user,
        due_date__date__gte=week_start,
        due_date__date__lte=week_end
    )
    week_total = week_tasks.count()
    week_completed = week_tasks.filter(completed=True).count()
    
    # Tasks due this month
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    month_tasks = Task.objects.filter(
        user=request.user,
        due_date__date__gte=month_start,
        due_date__date__lte=month_end
    )
    month_total = month_tasks.count()
    month_completed = month_tasks.filter(completed=True).count()
    
    # Calculate completion rates
    overall_completion_rate = (completed_tasks_count / all_tasks_count * 100) if all_tasks_count > 0 else 0
    week_completion_rate = (week_completed / week_total * 100) if week_total > 0 else 0
    month_completion_rate = (month_completed / month_total * 100) if month_total > 0 else 0
    
    # Calculate on-time completion rate (tasks completed before or on their due date)
    on_time_count = Task.objects.filter(
        user=request.user,
        completed=True,
        due_date__date__gte=timezone.now().date() - timedelta(days=30)
    ).annotate(
        is_on_time=Count('pk', filter=Q(completed=True))
    ).count()
    
    recent_completed = Task.objects.filter(
        user=request.user,
        completed=True,
        due_date__date__gte=timezone.now().date() - timedelta(days=30)
    ).count()
    
    on_time_rate = (on_time_count / recent_completed * 100) if recent_completed > 0 else 0
    
    # Tasks by priority
    high_priority = Task.objects.filter(user=request.user, priority='high').count()
    medium_priority = Task.objects.filter(user=request.user, priority='medium').count()
    low_priority = Task.objects.filter(user=request.user, priority='low').count()
    
    # Prepare JSON data for charts
    chart_data = {
        'labels': json.dumps(labels),
        'completion_data': json.dumps(completion_data),
        'creation_data': json.dumps(creation_data),
        'overdue_data': json.dumps(overdue_data),
        'priority_data': json.dumps([high_priority, medium_priority, low_priority])
    }
    
    context = {
        'chart_data': chart_data,
        'period': period,
        'overall_completion_rate': int(overall_completion_rate),
        'week_completion_rate': int(week_completion_rate),
        'month_completion_rate': int(month_completion_rate),
        'all_tasks_count': all_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'on_time_rate': int(on_time_rate),
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
    }
    
    return render(request, 'tasks/analytics.html', context)

@login_required
def pomodoro(request):
    """View for Pomodoro timer with task selection"""
    # Get user's incomplete tasks
    tasks = Task.objects.filter(
        user=request.user,
        completed=False
    ).order_by('due_date')
    
    context = {
        'tasks': tasks,
    }
    
    return render(request, 'tasks/pomodoro.html', context)
