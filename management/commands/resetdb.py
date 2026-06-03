from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from projects.models import Project
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
      email="admin@example.com", 
      password="admin",
      first_name="Alessio", # Or Christian...
      last_name="Zanetti"   # ...Yang
    )
    logger.info("Created admin.")

    #2. Creating 10 users.
    # Remainder: Thanks to the implemented signal, every time a user is created, its
    # root project is also automatically created.
    full_names = [
      {"first_name": "Alessio", "last_name": "Yang"},
      {"first_name": "Christian", "last_name": "Zanetti"},
      {"first_name": "Alessandro", "last_name": "Ferrari"},
      {"first_name": "Sofia", "last_name": "Esposito"},
      {"first_name": "Matteo", "last_name": "Bianchi"},
      {"first_name": "Chiara", "last_name": "Romano"},
      {"first_name": "Andrea", "last_name": "Colombo"},
      {"first_name": "Francesca", "last_name": "Ricci"},
      {"first_name": "Lorenzo", "last_name": "Marino"},
      {"first_name": "Alice", "last_name": "Greco"}
    ]
    users = []
    for full_name in full_names:
      first_name = full_name["first_name"]
      last_name = full_name["last_name"]
      username = f"{first_name.lower()}.{last_name.lower()}"
      users.append(User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="password123",
        first_name=first_name,
        last_name=last_name
      ))
    logger.info(f"Created {len(users)} users.")

    # 3. Creating the project structure for the first user.
    # Root
    #   University
    #     Web Technologies
    #     Compilers
    #       Part 1
    #       Part 2
    #     CyberChallenge.IT
    #   Gym
    #     Routine 1
    #     Routine 2
    #     Routine 3
    first_user = users[0]
    first_user_root = Project.objects.get(owner=first_user, parent=None)
    university_project = Project.objects.create(
      title="University",
      parent=first_user_root
    )
    web_technologies_project = Project.objects.create(
      title="Web Technologies",
      parent=university_project
    )
    compilers_project = Project.objects.create(
      title="Compilers",
      parent=university_project
    )
    part_1_compilers_project = Project.objects.create(
      title="Part 1",
      parent=compilers_project
    )
    part_2_compilers_project = Project.objects.create(
      title="Part 2",
      parent=compilers_project
    )
    cyberchallenge_it_project = Project.objects.create(
      title="CyberChallenge.IT",
      parent=university_project
    )
    gym_project = Project.objects.create(title="Gym", parent=first_user_root)
    routine_1_gym = Project.objects.create(title="Routine 1", parent=gym_project)
    routine_2_gym = Project.objects.create(title="Routine 2", parent=gym_project)
    routine_3_gym = Project.objects.create(title="Routine 3", parent=gym_project)
    logger.info("Created project structure for the first user.")

    logger.info("Database successfully reinitialized!")