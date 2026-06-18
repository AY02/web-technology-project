from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


# Where are LoginView and LogoutView?
# We don’t define them here! Our urls.py uses django.contrib.auth.urls,
# which automatically loads the framework’s default views.


class SignUpView(generic.CreateView):
  form_class = UserCreationForm
  success_url = reverse_lazy("profile")
  template_name = "accounts/register.html"

  def form_valid(self, form):
    """
    We override this method to automatically log in immediately after saving the new
    user in the database.
    """
    response = super().form_valid(form)
    login(self.request, self.object)
    return response

@login_required
def profile_view(request):
  return render(request, 'accounts/profile.html')