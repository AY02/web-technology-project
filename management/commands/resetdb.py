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

    # 2. Creating 4 users.
    # Remainder: Thanks to the implemented signal, every time a user is created, its
    # root project is also automatically created.
    full_names = [
      {"first_name": "Alessio", "last_name": "Yang"},
      {"first_name": "Christian", "last_name": "Zanetti"},
      {"first_name": "Marco", "last_name": "Dondi"},
      {"first_name": "Federico", "last_name": "Giansoldati"}
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
    root_0 = Project.objects.get(owner=users[0], parent=None)    
    university_0 = Project.objects.create(title="University", parent=root_0)
    web_technologies_0 = Project.objects.create(title="Web Technologies", parent=university_0)
    compilers_0 = Project.objects.create(title="Compilers", parent=university_0)
    part_1_compilers_0 = Project.objects.create(title="Part 1", parent=compilers_0)
    part_2_compilers_0 = Project.objects.create(title="Part 2", parent=compilers_0)
    cyberchallenge_it_0 = Project.objects.create(title="CyberChallenge.IT", parent=university_0)
    gym_0 = Project.objects.create(title="Gym", parent=root_0)
    routine_1_gym_0 = Project.objects.create(title="Routine 1", parent=gym_0)
    routine_2_gym_0 = Project.objects.create(title="Routine 2", parent=gym_0)
    routine_3_gym_0 = Project.objects.create(title="Routine 3", parent=gym_0)
    logger.info("Created project structure for the first user.")

    # 4. Creating the project structure for the second user.
    # Root
    #   University
    #     Compilers
    #       Part 1
    #     Machine Learning
    root_1 = Project.objects.get(owner=users[1], parent=None)
    university_1 = Project.objects.create(title="University", parent=root_1)
    compilers_1 = Project.objects.create(title="Compilers", parent=university_1)
    part_1_compilers_1 = Project.objects.create(title="Part 1", parent=compilers_1)
    machine_learning_1 = Project.objects.create(title="Machine Learning", parent=university_1)
    logger.info("Created project structure for the second user.")