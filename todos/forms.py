from django import forms
from .models import ToDoEntry

class ToDoEntryForm(forms.ModelForm):
    class Meta:
        model = ToDoEntry
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light', 
                'placeholder': 'Add a new task...',
                'required': True
            }),
        }