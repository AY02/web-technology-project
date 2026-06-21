from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectPermission
from django.utils import timezone
import datetime
from todos.models import ToDoEntry
import re


User = get_user_model()


class Command(BaseCommand):
  help = 'Clear the database and reinitialize it with default static records.'

  def handle(self, *args, **options):
    self.stdout.write('Emptying the database...')
    
    # Flushing the database without user confirmation.
    call_command('flush', interactive=False)
    
    self.stdout.write('Database emptied.')
    self.stdout.write('Creating static records...')

    # Creating the admin.
    admin = User.objects.create_superuser(
      username='admin', 
      email='admin@example.com', 
      password='admin',
      first_name='Alessio', # Or Christian...
      last_name='Zanetti'   # ...Yang
    )
    self.stdout.write('Created admin.')

    # Creating 6 users.
    # Remainder:
    # - Thanks to the implemented signal, every time a user is created, its root
    #   project is also automatically created.
    # - Similarly, whenever a project is created, its todo list is created.
    full_names = [
      {'first_name': 'Alessio', 'last_name': 'Yang'},         # 0
      {'first_name': 'Christian', 'last_name': 'Zanetti'},    # 1
      {'first_name': 'Federico', 'last_name': 'Giansoldati'}, # 2
      {'first_name': 'Marco', 'last_name': 'Dondi'},          # 3
      {'first_name': 'Luca', 'last_name': 'Ferretti'},        # 4
      {'first_name': 'Andrea', 'last_name': 'Corsini'},       # 5
      {'first_name': 'Mauro', 'last_name': 'Dell\'Amico'},    # 6
    ]
    users = []
    for full_name in full_names:
      first_name = full_name['first_name']
      last_name = full_name['last_name']
      # Remove anything that isn't a letter, number, underscore, or dot.
      username = f'{first_name.lower()}.{last_name.lower()}'
      username = re.sub(r'[^a-zA-Z0-9_.]', '', username)
      users.append(User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='password123',
        first_name=first_name,
        last_name=last_name
      ))
    self.stdout.write(f'Created {len(users)} users.')

    # Creating the project structure for the user Alessio Yang.
    # Root
    #   University
    #     Web Technologies
    #     Compilers
    #       Part 1
    #       Part 2
    #     CyberChallenge.IT
    #     Thesis
    #   Gym
    #     Routine 1
    #     Routine 2
    #     Routine 3
    #   Finance
    #   Open Source
    #     Ping Store App
    #     AlmostFS
    #     Portfolio
    root_0 = Project.objects.get(owner=users[0], parent=None)
    university_0 = Project.objects.create(title='University', parent=root_0)
    web_technologies_0 = Project.objects.create(title='Web Technologies', parent=university_0)
    compilers_0 = Project.objects.create(title='Compilers', parent=university_0)
    part_1_compilers_0 = Project.objects.create(title='Part 1', parent=compilers_0)
    part_2_compilers_0 = Project.objects.create(title='Part 2', parent=compilers_0)
    cyberchallenge_it_0 = Project.objects.create(title='CyberChallenge.IT', parent=university_0)
    thesis_0 = Project.objects.create(title='Thesis', parent=university_0)
    gym_0 = Project.objects.create(title='Gym', parent=root_0)
    routine_1_gym_0 = Project.objects.create(title='Routine 1', parent=gym_0)
    routine_2_gym_0 = Project.objects.create(title='Routine 2', parent=gym_0)
    routine_3_gym_0 = Project.objects.create(title='Routine 3', parent=gym_0)
    finance_0 = Project.objects.create(title='Finance', parent=root_0)
    open_source = Project.objects.create(title='Open Source', parent=root_0, visibility='pub')
    ping_store_app = Project.objects.create(title='Ping Store App', parent=open_source, visibility='pub')
    almost_fs_app = Project.objects.create(title='AlmostFS', parent=open_source, visibility='pub')
    portfolio_0 = Project.objects.create(title='Portfolio', parent=open_source, visibility='pub')
    self.stdout.write('Created project structure for the user Alessio Yang.')

    # Creating the project structure for the user Christian Zanetti.
    # Root
    #   University
    #     Compilers
    #       Part 1
    #     Machine Learning
    #   Thesis
    root_1 = Project.objects.get(owner=users[1], parent=None)
    university_1 = Project.objects.create(title='University', parent=root_1)
    compilers_1 = Project.objects.create(title='Compilers', parent=university_1)
    part_1_compilers_1 = Project.objects.create(title='Part 1', parent=compilers_1)
    machine_learning_1 = Project.objects.create(title='Machine Learning', parent=university_1)
    thesis_1 = Project.objects.create(title='Thesis', parent=university_1)
    self.stdout.write('Created project structure for the user Christian Zanetti.')

    # Creating the project structure for the user Federico Giansoldati.
    # Root
    #   University
    #     Software Project
    #   Portfolio
    root_2 = Project.objects.get(owner=users[2], parent=None)
    university_2 = Project.objects.create(title='University', parent=root_2)
    software_project_2 = Project.objects.create(title='Software Project', parent=university_2)
    portfolio_2 = Project.objects.create(title='Portfolio', parent=root_2, visibility='pub')
    self.stdout.write('Created project structure for the user Federico Giansoldati.')

    # Creating project permissions.
    # Christian Zanetti becomes a Collaborator on Alessio's 'Part 2', 'Web Technologies' and 'AlmostFS'.
    # Federico Giansoldati becomes a Viewer on Alessio's 'Compilers'.
    # Marco Dondi becomes a Viewer on Alessio's 'Compilers'.
    # Marco Dondi becomes a Collaborator on Federico's 'Software Project'.
    # Luca Ferretti becomes a Commentator on Alessio's Thesis.
    # Andrea Corsini becomes a Commentator on Christian's Thesis.
    # Mauro Dell'Amico becomes a Commentator on Christian's Thesis.
    ProjectPermission.objects.create(user=users[1], project=part_2_compilers_0, role='coll')
    ProjectPermission.objects.create(user=users[1], project=web_technologies_0, role='coll')
    ProjectPermission.objects.create(user=users[1], project=almost_fs_app, role='coll')
    ProjectPermission.objects.create(user=users[2], project=compilers_0, role='view')
    ProjectPermission.objects.create(user=users[3], project=compilers_0, role='view')
    ProjectPermission.objects.create(user=users[3], project=software_project_2, role='coll')
    ProjectPermission.objects.create(user=users[4], project=thesis_0, role='comm')
    ProjectPermission.objects.create(user=users[5], project=thesis_1, role='comm')
    ProjectPermission.objects.create(user=users[6], project=thesis_1, role='comm')
    self.stdout.write('Created project permissions.')

    # Creating todo entries for Alessio's 'Web Technologies'.
    web_tech_0_deadline = datetime.date(2026, 6, 22)
    today = timezone.now().date()
    web_tech_0_todo_entries = [
      ("Create and setup project", -30)
      ("Implement models", -29),
      ("Implement signals", -28),
      ("Implement resetdb command", -27),
      ("Create authentication system", -26),
      ("Create homepage and authentication UI", -25),
      ("Implement project CRUD", -24),
      ("Create dashboard, project sidebar and comment sidebar templates", -23),
      ("Implement todo entry CRUD", -22),
      ("Implement todo toggle with AJAX", -21),
      ("Implement document CRUD and template", -20),
      ("Implement comment CRUD and template", -19),
      ("Implement calendar view and template", -18),
      ("Implement pending edit system", -17),
      ("Create GUI for owner to assign permissions", -16),
      ("Create a search bar with suggestions for public projects using AJAX", -15),
      ("Create GUI to show edit history on a document", -14),
      ("Create GUI for permission assignment", -13)
    ]

    for todo_entry, days_offset in web_tech_0_todo_entries:
      task_deadline = web_tech_0_deadline + datetime.timedelta(days=days_offset)
      ToDoEntry.objects.create(
        todo_list=web_technologies_0.todolist,
        content=todo_entry,
        deadline=task_deadline,
        is_completed=True,
        completion_date=task_deadline
      )

    self.stdout.write(self.style.SUCCESS('Database successfully reinitialized!'))