from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
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


class DocumentDetailView(LoginRequiredMixin, DetailView):
  model = Document
  template_name = 'documents/document_detail.html'
  context_object_name = 'document'

  def dispatch(self, request, *args, **kwargs):
    """Security check for users visibility on the project of the document."""
    doc = self.get_object()
    if not doc.project_parent.can_view(request.user):
      raise Http404("You do not have permission to view this document.")
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    """Permissions to show/hide Edit/Delete buttons in the template."""
    context = super().get_context_data(**kwargs)
    doc = self.get_object()
    context['is_owner'] = doc.is_owner(self.request.user)
    context['can_propose'] = doc.can_propose_edit(self.request.user)
    return context


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
  model = Document
  form_class = DocumentForm
  template_name = 'documents/document_form.html'

  def dispatch(self, request, *args, **kwargs):
    """Only the owner can directly edit the document."""
    doc = self.get_object()
    if not doc.is_owner(request.user):
      raise Http404("Only the owner can directly edit the document.")
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['project'] = self.get_object().project_parent
    context['is_update'] = True 
    return context

  def get_success_url(self):
    messages.success(self.request, "Document updated successfully.")
    return reverse('documents:document_detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
  model = Document
  template_name = 'documents/document_confirm_delete.html'

  def dispatch(self, request, *args, **kwargs):
    """Only the owner can delete the document."""
    doc = self.get_object()
    if not doc.is_owner(request.user):
      raise Http404("Only the owner can delete this document.")
    return super().dispatch(request, *args, **kwargs)

  def get_success_url(self):
    project_id = self.get_object().project_parent.id
    messages.success(self.request, "Document deleted successfully.")
    return reverse('dashboard_project', kwargs={'project_id': project_id})