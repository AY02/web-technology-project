from django.urls import path, include
from .views import SignUpView, profile_view


# We are not including the routes for logging in and out because they already exist
# in Django’s native routes.
urlpatterns = [
  path('register/', SignUpView.as_view(), name='register'),
  path('profile/', profile_view, name='profile'),
  # It includes /accounts/[login|logout|password_change|password_reset].
  path('', include('django.contrib.auth.urls'))
]