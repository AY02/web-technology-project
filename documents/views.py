from django.views.generic.edit import CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin

from projects.models import Project
from .models import Document
from .forms import DocumentForm


class DocumentCreateView(LoginRequiredMixin, CreateView):
  model = Document
  form_class = DocumentForm
  template_name = 'documents/document_form.html' 

  def dispatch(self, request, *args, **kwargs):
    """Security check before uploading the view."""
    self.project = get_object_or_404(Project, id=self.kwargs['project_id'])
    if not self.project.can_edit_todo_document(request.user):
      raise Http404("You do not have permission to create documents here.")
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    """Passing the project to the template for the return to the project logic."""
    context = super().get_context_data(**kwargs)
    context['project'] = self.project
    return context

  def form_valid(self, form):
    """Checking validity of the form."""
    form.instance.project_parent = self.project
    messages.success(self.request, f"Document '{form.instance.title}' created.")
    return super().form_valid(form)

  def get_success_url(self):
    """Redirecting to the dashboard project after the save."""
    return reverse('dashboard_project', kwargs={'project_id': self.project.id})
