from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class Profile(models.Model):
    MAJOR_CHOICES = [
        ('computer_science', 'Computer Science'),
        ('engineering', 'Engineering'),
        ('business', 'Business'),
        ('finance', 'Finance'),
        ('psychology', 'Psychology'),
        ('medicine', 'Medicine'),
        ('arts', 'Arts'),
        ('education', 'Education'),
        ('law', 'Law'),
        ('other', 'Other'),
    ]
    
    DEGREE_CHOICES = [
        ('bachelors', 'Bachelor\'s Degree'),
        ('masters', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    major = models.CharField(max_length=50, choices=MAJOR_CHOICES, blank=True, null=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    image = models.CharField(max_length=255, default='default.jpg')
    instagram = models.CharField(max_length=30, blank=True, null=True, help_text="Your Instagram username (without @)")
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_image_url(self):
        # Check if the image file exists
        file_path = os.path.join('media', self.image)
        if os.path.exists(file_path):
            return f'/media/{self.image}'
        else:
            # Return a default placeholder URL
            return '/static/img/default_avatar.png'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
