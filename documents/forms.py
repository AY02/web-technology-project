from django import forms
from .models import Document, PendingEdit

class DocumentForm(forms.ModelForm):
  class Meta:
    model = Document
    fields = ['title', 'content']
    widgets = {
      'title': forms.TextInput(attrs={
        'class': 'form-control form-control-lg bg-light border-0 mb-3', 
        'placeholder': 'Document Title (e.g. Appunti_Lezione)'
      }),
      'content': forms.Textarea(attrs={
        'class': 'form-control bg-light border-0', 
        'rows': 15, 
        'placeholder': 'Start writing your document here...'
      }),
    }

class PendingEditForm(forms.ModelForm):
  class Meta:
    model = PendingEdit
    # The user can only modifies title and content
    fields = ['modified_title', 'modified_content']
    widgets = {
      'modified_title': forms.TextInput(attrs={
        'class': 'form-control form-control-lg bg-light border-0 mb-3', 
        'placeholder': 'Proposed Title'
      }),
      'modified_content': forms.Textarea(attrs={
        'class': 'form-control bg-light border-0', 
        'rows': 15, 
        'placeholder': 'Propose your changes here...'
      }),
    }