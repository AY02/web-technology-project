from django.test import TestCase
from django.core.exceptions import ValidationError
from todos.models import ToDoList, ToDoEntry
from accounts.models import User
from projects.models import Project

# Create your tests here.

class BasicToDoModelsTests(TestCase):
  
  # Set up user, root, project, and todolist
  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='password')
    self.root = Project.objects.get(owner=self.user, parent=None)
    self.project = Project.objects.create(owner=self.user, title='My Project', parent=self.root)
    self.todo_list = self.project.todolist # todolist created by the project signal
  
  # BASIC test: todo entry created successfully and set to incomplete by default
  def test_todo_entry_creation_success(self):
    entry = ToDoEntry.objects.create(todo=self.todo_list, content='Buy milk')
    self.assertFalse(entry.is_completed)
    self.assertEqual(ToDoEntry.objects.count(), 1)
  
  # BASIC test: content longer than models' limit (256)
  def test_todo_entry_content_exceeds_max_length(self):
    too_long_content = 'A' * 300
    entry = ToDoEntry(todo=self.todo_list, content=too_long_content)
    # full_clean() should raise a ValidationError because of max_length limits
    with self.assertRaises(ValidationError):
      entry.full_clean()