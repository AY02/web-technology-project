from django.test import TestCase
from django.urls import reverse

# Create your tests here.
class BasicAuthenticationTests(TestCase):
  
  # BASIC test for unauthenticated user, who attempts to get 
  # the dashboard view without logging in, the test checks that 
  # the server responds with a 302 redirect to the login page
  def test_unauthenticated_user_redirected_from_dashboard(self):
    response = self.client.get(reverse('dashboard'))
    self.assertEqual(response.status_code, 302)
    self.assertTrue(response.url.startswith(reverse('login')))