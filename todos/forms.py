from django import forms
from .models import ToDoEntry

class ToDoEntryForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
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
      'deadline': forms.DateTimeInput(attrs={
        'class': 'form-control border-0 bg-light',
        'type': 'datetime-local'
      }),
    }
    
  def clean(self):
    cleaned_data = super().clean()
    content = cleaned_data.get("content")
    deadline = cleaned_data.get("deadline")

    # Check anti duplicates
    if self.todo_list and content:
      exists = ToDoEntry.objects.filter(
        todo=self.todo_list,
        content=content,
        deadline=deadline
        ).exists()
      if exists:
        raise forms.ValidationError("A task with this content and deadline already exists in this list.")
   
    return cleaned_data