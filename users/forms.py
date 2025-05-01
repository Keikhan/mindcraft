from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
import os

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    image = forms.FileField(required=False)
    age = forms.IntegerField(min_value=0, max_value=120, required=False, 
                           help_text="Optional: Your age for personalized recommendations")
    
    class Meta:
        model = Profile
        fields = ['major', 'degree', 'location', 'age', 'instagram']
        labels = {
            'major': 'Field of Study/Major',
            'degree': 'Degree Level',
            'location': 'Location',
            'age': 'Age',
            'instagram': 'Instagram Username',
        }
        help_texts = {
            'major': 'Select your field of study or profession',
            'degree': 'Select your highest level of education',
            'location': 'Where are you located?',
            'instagram': 'Your Instagram username (without @)',
        }
        
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Handle file upload manually
        if 'image' in self.files:
            uploaded_file = self.files['image']
            # Create a path relative to the media directory
            filename = f'profile_pics/{profile.user.username}_{uploaded_file.name}'
            file_path = os.path.join('media', filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the file
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
                    
            # Update the image field with the relative path
            profile.image = filename
        
        if commit:
            profile.save()
        return profile 