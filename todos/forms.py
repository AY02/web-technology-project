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
      'deadline': forms.DateInput(attrs={
        'class': 'form-control border-0 bg-light',
        'type': 'date'
      }),
    }
    
  def clean(self):
    cleaned_data = super().clean()
    content = cleaned_data.get("content")
    deadline = cleaned_data.get("deadline")

    # Check anti duplicates
    if self.todo_list and content:
      same_name = ToDoEntry.objects.filter(
        todo=self.todo_list,
        content=content
        )
      
      if self.instance and self.instance.pk:
        same_name = same_name.exclude(pk=self.instance.pk)
      if same_name.exists():
        raise forms.ValidationError("A task with this name already exists in this list.")
   
    return cleaned_data