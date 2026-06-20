from django import forms
from .models import Project, ProjectPermission


class ProjectCreateForm(forms.ModelForm):
  def __init__(self, user=None, parent_project=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # By inserting user and project parent in the internal instance of the form, the
    # clean() method in models.py will find them and won't crash.
    if user and parent_project:
      self.instance.owner = user
      self.instance.parent = parent_project

  class Meta:
    model = Project
    # The user only choses title and visibility, while parent and owner are managed
    # in the backend automatically.
    fields = ['title', 'visibility']
    widgets = {
      'title': forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'e.g., Algorithms'}
      ),
      'visibility': forms.Select(attrs={'class': 'form-select'}),
    }


class ProjectEditForm(forms.ModelForm):
  class Meta:
    model = Project
    fields = ['title', 'visibility']
    widgets = {
      'title': forms.TextInput(attrs={'class': 'form-control'}),
      'visibility': forms.Select(attrs={'class': 'form-select'}),
    }


class AddPermissionForm(forms.Form):
  username = forms.CharField(
    max_length=150, 
    widget=forms.TextInput(attrs={
      'class': 'form-control', 
      'placeholder': 'Enter exact username (e.g. christian.zanetti)'
    })
  )
  role = forms.ChoiceField(
    choices=ProjectPermission.ROLE_CHOICES,
    widget=forms.Select(attrs={'class': 'form-select'})
  )