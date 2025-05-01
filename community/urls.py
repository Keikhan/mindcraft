from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('user/<str:username>/', views.user_profile, name='community_user_profile'),
] 