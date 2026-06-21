from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectPermission


User = get_user_model()


class Command(BaseCommand):
  help = "Clear the database and reinitialize it with default static records."

  def handle(self, *args, **options):
    self.stdout.write("Emptying the database...")
    
    # Flushing the database without user confirmation.
    call_command("flush", interactive=False)
    
    self.stdout.write("Database emptied.")
    self.stdout.write("Creating static records...")

    # 1. Creating the admin.
    admin = User.objects.create_superuser(
      username="admin", 
      email="admin@example.com", 
      password="admin",
      first_name="Alessio", # Or Christian...
      last_name="Zanetti"   # ...Yang
    )
    self.stdout.write("Created admin.")

    # 2. Creating 4 users.
    # Remainder: Thanks to the implemented signal, every time a user is created, its
    # root project is also automatically created.
    full_names = [
      {"first_name": "Alessio", "last_name": "Yang"},
      {"first_name": "Christian", "last_name": "Zanetti"},
      {"first_name": "Federico", "last_name": "Giansoldati"},
      {"first_name": "Marco", "last_name": "Dondi"}
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
    self.stdout.write(f"Created {len(users)} users.")

    # 3. Creating the project structure for the user Alessio Yang.
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
    self.stdout.write("Created project structure for the user Alessio Yang.")

    # 4. Creating the project structure for the user Christian Zanetti.
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
    self.stdout.write("Created project structure for the user Christian Zanetti.")

    # 5. Creating the project structure for the user Federico Giansoldati.
    # Root
    #   Software Project
    root_2 = Project.objects.get(owner=users[2], parent=None)
    software_project_2 = Project.objects.create(title="Software Project", parent=root_2)
    self.stdout.write("Created project structure for the user Federico Giansoldati.")

    # 6. Creating project permissions.
    # Alessio Yang becomes a Commentator on Federico's "Software Project".
    # Christian Zanetti becomes a Collaborator on Alessio's "Part 2" and "Web Technologies".
    # Marco Dondi becomes a Viewer on Alessio's "Compilers".
    # Marco Dondi becomes a Collaborator on Federico's "Software Project".
    ProjectPermission.objects.create(user=users[0], project=software_project_2, role="comm")
    ProjectPermission.objects.create(user=users[1], project=part_2_compilers_0, role="coll")
    ProjectPermission.objects.create(user=users[1], project=web_technologies_0, role="coll")
    ProjectPermission.objects.create(user=users[3], project=compilers_0, role="view")
    ProjectPermission.objects.create(user=users[3], project=software_project_2, role="coll")
    self.stdout.write("Created project permissions.")

    # 7. Creating PUBLIC projects to test the Live Search disambiguation.
    # We will intentionally use duplicate titles across different users to test the search bar.
    # Marco Dondi's public projects.
    root_3 = Project.objects.get(owner=users[3], parent=None)
    open_source_contrib_3 = Project.objects.create(title="Open Source Contributions", parent=root_3, visibility="pub")
    web_technologies_3 = Project.objects.create(title="Web Technologies", parent=root_3, visibility="pub")
    Project.objects.create(title="Notes", parent=web_technologies_3, visibility="pub") # Nested public
    machine_learning_3 = Project.objects.create(title="Machine Learning", parent=root_3, visibility="pub")

    # Federico Giansoldati's public projects
    machine_learning_2 = Project.objects.create(title="Machine Learning", parent=root_2, visibility="pub")
    Project.objects.create(title="Neural Networks", parent=machine_learning_2, visibility="pub")

    # Alessio Yang's public projects
    portfolio_0 = Project.objects.create(title="Public Portfolio", parent=root_0, visibility="pub")
    Project.objects.create(title="Web Technologies", parent=portfolio_0, visibility="pub")

    # Christian Zanetti's public projects
    portfolio_1 = Project.objects.create(title="Public Portfolio", parent=root_1, visibility="pub")
    Project.objects.create(title="Open Source Contributions", parent=portfolio_1, visibility="pub")
    
    self.stdout.write("Created public projects for search testing.")

    self.stdout.write(self.style.SUCCESS("Database successfully reinitialized!"))