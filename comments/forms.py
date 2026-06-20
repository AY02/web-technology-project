from django import forms
from .models import Comment

# Used to validate the text sent
class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields = ['content']