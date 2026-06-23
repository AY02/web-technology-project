from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from accounts.models import User
from projects.models import Project, ProjectPermission
from documents.models import Document, PendingEdit

# Create your tests here.

class BasicDocumentTests(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='password')
    self.root = Project.objects.get(owner=self.user, parent=None)

  def test_document_creation_success(self):
    doc = Document.objects.create(
      project_parent=self.root,
      title='My first document',
      content='Hello World!'
    )
    # Check that the document was saved into the database
    self.assertEqual(Document.objects.count(), 1)
    self.assertEqual(doc.title, 'My first document')

  def test_document_requires_title(self):
    doc = Document(
      project_parent=self.root, 
      title='', 
      content='Some content'
    )
    with self.assertRaises(ValidationError):
      doc.full_clean()


class PendingEditWorkflowTests(TestCase):
  def setUp(self):
    # Create the owner, a collaborator, and an unauthorized stranger
    self.owner = User.objects.create_user(username='owner', password='pwd')
    self.collaborator = User.objects.create_user(username='collab', password='pwd')
    self.stranger = User.objects.create_user(username='stranger', password='pwd')
    # Getting the auto-generated root project for the owner
    self.root = Project.objects.get(owner=self.owner, parent=None)
    # Create the original document
    self.doc = Document.objects.create(
      project_parent=self.root, 
      title='Original Title', 
      content='Original Content'
    )
    # Assign the collaborator role to the 'collab' user
    ProjectPermission.objects.create(
      user=self.collaborator, 
      project=self.root, 
      role='coll'
    )
  
  # NON BASIC test, stressing the application from the login of a 
  # user that proposes an edit, to the acceptance of the owner of the document's
  # parent project, also checking whether an unauthorized user can accept the pending 
  def test_end_to_end_edit_proposal_and_acceptance(self):
    # collaborator logs in and edits proposal
    self.client.login(username='collab', password='pwd')
    response = self.client.post(
      reverse('documents:propose_edit', kwargs={'document_id': self.doc.id}),
      {'modified_title': 'New Title', 'modified_content': 'New Content'}
    )
    # Checking server redirect after the proposal
    self.assertEqual(response.status_code, 302)
    # The pending edit now must exist in the database and needs to be in pending state
    pending_edit = PendingEdit.objects.get(document=self.doc)
    self.assertEqual(pending_edit.state, 'pen')
    self.assertEqual(pending_edit.modified_title, 'New Title')

    # Unauthorized user tries to accept the edit
    self.client.login(username='stranger', password='pwd')
    response_unauth = self.client.post(
      reverse('documents:handle_edit', kwargs={'edit_id': pending_edit.id, 'action': 'accept'})
    )
    # Unauthorized user blocked
    self.assertEqual(response_unauth.status_code, 404)

    # Owner logs in and accepts the edit
    self.client.login(username='owner', password='pwd')
    response_owner = self.client.post(
      reverse('documents:handle_edit', kwargs={'edit_id': pending_edit.id, 'action': 'accept'}),
      follow=True # to follow the redirect to verify the final page
    )
    # Checking that the request was successful, and verifying the
    # outcome on the database models
    self.assertEqual(response_owner.status_code, 200)
    self.doc = Document.objects.get(id=self.doc.id)
    pending_edit = PendingEdit.objects.get(document=self.doc)
    self.assertEqual(pending_edit.state, 'acc')
    self.assertEqual(self.doc.title, 'New Title')
    self.assertEqual(self.doc.content, 'New Content')
    # Checking the proposal appears in the history view section
    history_url = reverse('documents:edit_history', args=[self.root.id])
    response = self.client.get(history_url)
    self.assertIn(pending_edit, response.context['historical_edits'])