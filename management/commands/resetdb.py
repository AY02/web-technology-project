from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
  help = "Clear the database and reinitialize it with default static records."

  def handle(self, *args, **options):
    logger.info("Emptying the database...")
    
    # Flushing the database without user confirmation.
    call_command("flush", interactive=False)
    
    logger.info("Database emptied.")
    logger.info("Creating static records...")

    # 1. Creating the admin.
    admin = User.objects.create_superuser(
      username="admin", 
      email="admin@admin.admin", 
      password="admin",
      first_name="admin",
      last_name="admin"
    )
    logger.info("Created admin.")

    #2. Creating 10 users.
    # Remainder: Thanks to the implemented signal, every time a user is created, its
    # root project is also automatically created.
    first_names = ["Marco", "Giulia", "Alessandro", "Sofia", "Matteo", "Chiara",
                   "Andrea", "Francesca", "Lorenzo", "Alice"]
    last_names = ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano",
                  "Colombo", "Ricci", "Marino", "Greco"]
    users = []
    for i in range(10):
      first_name = first_names[i]
      last_name = last_names[i]
      username = first_name.lower() + '.' + last_name.lower()
      users.append(User.objects.create_user(
        username=username,
        email=username + "@example.com",
        password="password123",
        first_name=first_name,
        last_name=last_name
      ))
    logger.info(f"Created {len(users)} users.")

    logger.info("Database successfully reinitialized!")