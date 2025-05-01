# MindCraft Django Website

A Django website with user authentication and profile management. This project allows users to register, login, and manage their profiles with CRUD functionality.

## Features

- User registration and authentication
- User profile management (CRUD operations)
- Responsive design with Bootstrap
- Admin panel for user management

## Requirements

- Python 3.8+
- Django 5.2+
- django-widget-tweaks 1.5+

## Setup

1. Clone the repository:
```
git clone <repository-url>
cd django_mindcraft
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run migrations:
```
python manage.py migrate
```

5. Create a superuser (admin):
```
python manage.py createsuperuser
```

6. Run the development server:
```
python manage.py runserver
```

7. Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

## Project Structure

- `midcraft/` - Project settings and main URL configuration
- `users/` - User authentication and profile management app
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)
- `media/` - User-uploaded files

## Usage

1. Register a new account at `/users/register/`
2. Log in at `/users/login/`
3. View and edit your profile at `/users/profile/`
4. Log out at `/users/logout/`
5. Access the admin panel at `/admin/` 