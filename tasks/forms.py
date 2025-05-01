from django import forms
from .models import Task
from django.utils import timezone
import datetime

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    
    due_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text="Optional: Set a specific time for this task"
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If we have an instance with a due_date, split it into date and time components
        if self.instance.pk and self.instance.due_date:
            self.fields['due_date'].initial = self.instance.due_date.date()
            self.fields['due_time'].initial = self.instance.due_date.time()
    
    def save(self, commit=True):
        task = super().save(commit=False)
        
        # Combine date and time fields if provided
        date_value = self.cleaned_data.get('due_date')
        time_value = self.cleaned_data.get('due_time')
        
        if date_value:
            if time_value:
                # If both date and time are provided, combine them
                combined_datetime = datetime.datetime.combine(date_value, time_value)
                task.due_date = timezone.make_aware(combined_datetime)
            else:
                # If only date is provided, set time to midnight
                combined_datetime = datetime.datetime.combine(date_value, datetime.time.min)
                task.due_date = timezone.make_aware(combined_datetime)
        else:
            task.due_date = None
            
        if commit:
            task.save()
        return task 