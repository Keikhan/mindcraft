from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'priority', 'completed')
    list_filter = ('completed', 'priority', 'due_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'

admin.site.register(Task, TaskAdmin)
