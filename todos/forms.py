from django import forms
from .models import ToDoEntry


class ToDoEntryForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    # Preserve the todo_list attribute, which does not exist in the ModelForm class.
    self.todo_list = kwargs.pop('todo_list', None)
    super().__init__(*args, **kwargs)

  class Meta:
    model = ToDoEntry
    fields = ['content', 'deadline']
    widgets = {
      'content': forms.TextInput(attrs={
        'class': 'form-control border-0 bg-light', 
        'placeholder': 'Add a new task...',
        'required': True
      }),
      'deadline': forms.DateInput(attrs={
        'class': 'form-control border-0 bg-light flatpickr-date',
        'placeholder': 'Add deadline (opt)...',
        'type': 'date'
      })
    }