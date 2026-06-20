from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project
from .models import Document, PendingEdit
from .forms import DocumentForm, PendingEditForm


class DocumentCreateView(LoginRequiredMixin, CreateView):
  model = Document
  form_class = DocumentForm
  template_name = 'documents/document_form.html' 

  def dispatch(self, request, *args, **kwargs):
    """Security check before uploading the view."""
    self.project = get_object_or_404(Project, id=self.kwargs['project_id'])
    if not request.user.can_edit_document_in(self.project):
      raise Http404('You do not have permission to create documents here.')
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
  pk_url_kwarg = 'id'

  def dispatch(self, request, *args, **kwargs):
    """Security check for users visibility on the project of the document."""
    doc = self.get_object()
    if not request.user.can_view(doc.project_parent):
      raise Http404('You do not have permission to view this document.')
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    """Permissions to show/hide Edit/Delete buttons in the template."""
    context = super().get_context_data(**kwargs)
    doc = self.get_object()
    user = self.request.user
    context['can_edit_document'] = user.can_edit_document_in(doc.project_parent)
    context['can_propose_edit'] = user.can_propose_edit_of(doc)
    
    # If the user can propose, we check if there is already a pending edit.
    if context['can_propose_edit']:
      pending_edit = doc.pending_edits.filter(collaborator=user, state='pen').first()
      context['user_pending_edit'] = pending_edit
    # Check if the owner has pending edits
    if context['can_edit_document'] and user.is_owner_of(doc.project_parent):
      context['pending_edits_count'] = doc.pending_edits.filter(state='pen').count()
    
    return context


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
  model = Document
  form_class = DocumentForm
  template_name = 'documents/document_form.html'
  pk_url_kwarg = 'id'

  def dispatch(self, request, *args, **kwargs):
    """Only the owner can directly edit the document."""
    doc = self.get_object()
    if not request.user.can_edit_document_in(doc.project_parent):
      raise Http404('Only the owner can directly edit the document.')
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['project'] = self.get_object().project_parent
    context['is_update'] = True
    return context

  def get_success_url(self):
    messages.success(self.request, 'Document updated successfully.')
    return reverse('documents:document_detail', kwargs={'id': self.object.id})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
  model = Document
  template_name = 'documents/document_confirm_delete.html'
  pk_url_kwarg = 'id'

  def dispatch(self, request, *args, **kwargs):
    """Only the owner can delete the document."""
    doc = self.get_object()
    if not request.user.can_edit_document_in(doc.project_parent):
      raise Http404('Only the owner can delete this document.')
    return super().dispatch(request, *args, **kwargs)

  def get_success_url(self):
    project_id = self.get_object().project_parent.id
    messages.success(self.request, 'Document deleted successfully.')
    return reverse('dashboard_project', kwargs={'project_id': project_id})
  

class ProposeEditView(LoginRequiredMixin, UpdateView):
  model = PendingEdit
  form_class = PendingEditForm
  template_name = 'documents/document_form.html'

  def get_object(self):
    """Searches for pending drafts, otherwise it creates it."""
    self.document = get_object_or_404(Document, id=self.kwargs['document_id'])

    if not self.request.user.can_propose_edit_of(self.document):
      raise Http404('You do not have permission to propose edits to this document.')
        
    obj, created = PendingEdit.objects.get_or_create(
      document=self.document,
      collaborator=self.request.user,
      state='pen',
      # The defaults are the original title and content of the document.
      defaults={
        'modified_title': self.document.title,
        'modified_content': self.document.content
      }
    )
    return obj

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Variables for the correct use of the templates.
    context['project'] = self.document.project_parent
    context['document'] = self.document
    context['is_proposal'] = True
    return context

  def form_valid(self, form):
    messages.success(self.request, 'Your edit proposal has been saved and is waiting for review.')
    return super().form_valid(form)

  def get_success_url(self):
    return reverse('documents:document_detail', kwargs={'id': self.document.id})
  

# Owner's pending logic.
class ReviewEditsView(LoginRequiredMixin, ListView):
  model = PendingEdit
  template_name = 'documents/review_edits.html'
  context_object_name = 'pending_edits'

  def dispatch(self, request, *args, **kwargs):
    self.project = get_object_or_404(Project, id=self.kwargs['project_id'])
    if not request.user.can_edit_document_in(self.project):
      raise Http404('Only the project owner can review edits.')
    return super().dispatch(request, *args, **kwargs)

  def get_queryset(self):
    """Filtering pending edit for this document. If there is a 'doc'' 
    parameter, we filter only for the pending edits for that document"""
    queryset = PendingEdit.objects.filter(
      document__project_parent=self.project,
      state='pen'
    ).select_related('document', 'collaborator').order_by('-creation_date')
    
    doc_id = self.request.GET.get('doc')
    if doc_id:
      queryset = queryset.filter(document_id=doc_id)
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['project'] = self.project
    # eventual filtered doc id
    context['filtered_doc_id'] = self.request.GET.get('doc')
    # filtering only the documents of this project with pendings waiting
    context['documents_with_edits'] = Document.objects.filter(
      project_parent=self.project,
      pending_edits__state='pen'
    ).distinct()
    return context


@login_required
@require_POST
def handle_pending_edit(request, edit_id, action):
  """
  Handles the acceptance or the rejection of a proposal, given an action from the URL
  ('accept' or 'reject') using the model's methods.
  """
  pending_edit = get_object_or_404(PendingEdit, id=edit_id)
  project = pending_edit.document.project_parent

  if not request.user.can_edit_document_in(project):
    raise Http404('Only the owner can handle edits.')

  if action == 'accept':
    pending_edit.accept()
    messages.success(
      request,
      f"Changes applied to '{pending_edit.document.title}'."
    )
  elif action == 'reject':
    pending_edit.reject()
    messages.info(
      request,
      f"Proposed changes to '{pending_edit.document.title}' were rejected."
    )
  else:
    raise Http404('Invalid action.')

  return redirect('documents:review_edits', project_id=project.id)