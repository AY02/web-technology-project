from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectPermission
from django.utils import timezone
from todos.models import ToDoEntry
from documents.models import Document
from comments.models import Comment
import re, datetime


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
      ('Alessio', 'Yang'),          # 0
      ('Christian', 'Zanetti'),     # 1
      ('Federico', 'Giansoldati'),  # 2
      ('Marco', 'Dondi'),           # 3
      ('Luca', 'Ferretti'),         # 4
      ('Andrea', 'Corsini'),        # 5
      ('Mauro', "Dell'Amico")       # 6
    ]
    users = []
    for first_name, last_name in full_names:
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
    web_tech_0_deadline = timezone.make_aware(datetime.datetime(2026, 6, 22, 0, 0, 0))
    today = timezone.now()
    web_tech_0_todo_entries = [
      ('Create and setup project', -30),
      ('Implement models', -29),
      ('Implement signals', -28),
      ('Implement resetdb command', -27),
      ('Create authentication system', -26),
      ('Create homepage and authentication UI', -25),
      ('Implement project CRUD', -24),
      ('Create dashboard, project sidebar and comment sidebar templates', -23),
      ('Implement todo entry CRUD', -22),
      ('Implement todo toggle with AJAX', -21),
      ('Implement document CRUD and template', -20),
      ('Implement comment CRUD and template', -19),
      ('Implement calendar view and template', -18),
      ('Implement pending edit system', -17),
      ('Create GUI for owner to assign permissions', -16),
      ('Create a search bar with suggestions for public projects using AJAX', -15),
      ('Create GUI to show edit history on a document', -14),
      ('Create GUI for permission assignment', -13)
    ]
    for todo_entry, days_offset in web_tech_0_todo_entries:
      deadline = web_tech_0_deadline + datetime.timedelta(days=days_offset)
      is_completed = deadline < today
      completion_date = deadline if is_completed else None
      ToDoEntry.objects.create(
        todo=web_technologies_0.todolist,
        content=todo_entry,
        deadline=deadline,
        is_completed=is_completed,
        completion_date=completion_date
      )
    self.stdout.write("Created Alessio's Web Technologies todo entries.")

    # Creating documents for Alessio's 'Web Technologies'.
    web_tech_0_documents = [
      (
        'Project Requirements & Specifications', 
        'Overview of AlmostFS features: hierarchical projects, permission inheritance, todo lists, and collaborative document editing using Django.'
      ),
      (
        'Database Schema Design', 
        'Entity-Relationship notes. Project has a 1-to-1 with ToDoList. ToDoList has a 1-to-N with ToDoEntry. Users have a M-to-N with Projects through ProjectPermission.'
      ),
      (
        'Django Signals Implementation', 
        'Documentation on the post_save signals used to automatically generate the root project for new users and ToDoLists for new projects without raising IntegrityErrors.'
      ),
      (
        'Bootstrap 5 UI/UX Guidelines', 
        'Design system notes. Cards used for layout. Flexbox utilized heavily (flex-grow, flex-shrink) for responsive list items, sidebars, and text truncation.'
      ),
      (
        'Authentication & Security', 
        'User model overrides and security. Ensured passwords are hashed using create_user. Implemented login, logout, and registration forms inheriting from UserCreationForm.'
      ),
      (
        'AJAX Endpoints Documentation', 
        'Details on the asynchronous JavaScript calls used for toggling To-Do entries dynamically without reloading the page. CSRF tokens are carefully passed in the headers.'
      ),
      (
        'Permission Hierarchy Algorithm', 
        "Logic for calculating 'effective' roles. If a user is a Collaborator on a parent project, the system must traverse the tree to propagate visibility and permissions."
      ),
      (
        'Pending Edits System Logic', 
        'How document reviews work. Edits are saved in a temporary state until the project owner or a qualified collaborator approves them via the review dashboard.'
      ),
      (
        'ResetDB Command Notes', 
        'Custom management command to flush the database and repopulate it with static test data, maintaining realistic timezone-aware dates (timezone.make_aware).'
      ),
      (
        'Final Exam Presentation Pitch', 
        'Key talking points for the presentation. Focus heavily on the custom permissions engine, the database constraints (UniqueConstraint), and the seamless AJAX integrations.'
      )
    ]
    for title, content in web_tech_0_documents:
      Document.objects.create(project_parent=web_technologies_0, title=title, content=content) 
    self.stdout.write("Created Alessio's Web Technologies documents.")

    # Creating comments between Alessio and Christian for 'Web Technologies'.
    web_tech_0_comments = [
      (users[0], "Ho appena pushato i modelli base per i progetti e le todolist. Dacci un'occhiata quando puoi.", -29),
      (users[1], "Visti. Ottima l'idea della relazione OneToOne per le todolist, ci risparmia un sacco di query inutili.", -28),
      (users[0], "Esatto. Tra l'altro ho aggiunto i constraint per i nomi duplicati sui task, così blindiamo il database a livello di ORM.", -28),
      (users[1], 'Ho notato che il signal per la creazione automatica della root e delle liste funziona bene. Ma cosa succede se eliminiamo un utente?', -26),
      (users[0], "Tutto l'albero va in CASCADE e si pulisce da solo. Ho fatto un paio di test in console e sembra reggere perfettamente.", -26),
      (users[1], "Ottimo. Senti, per l'autenticazione usiamo il form standard di Django o ne facciamo uno custom?", -24),
      (users[0], 'Facciamo un custom form che eredita da UserCreationForm, altrimenti le password ci finiscono in chiaro nel db (storia vera, ci stavo per cascare ahah).', -24),
      (users[1], 'Ahah, il classico errore da manuale. Va bene, mi occupo io del template di login con Bootstrap 5.', -23),
      (users[0], 'Ho sistemato il comando resetdb. Ora genera anche le scadenze dinamiche usando timezone.make_aware, niente più warning gialli.', -21),
      (users[1], 'Meno male! Quei warning sui fusi orari mi stavano distruggendo gli occhi nel terminale ogni volta che rigeneravo il db.', -21),
      (users[1], "Sulla dashboard, la barra laterale dei progetti non prende tutta l'altezza dello schermo. Provo a sistemarla con flex-grow.", -18),
      (users[0], "Attento, usa 'min-height: 0' sul contenitore della lista, altrimenti Flexbox sbrocca quando c'è l'overflow. Ci ho sbattuto la testa ieri.", -18),
      (users[1], 'Perfetto, ha funzionato al primo colpo! Ho anche aggiunto il text-truncate per i titoli dei documenti troppo lunghi.', -17),
      (users[0], 'La vista per il toggle dei task in AJAX è pronta. Ho usato onchange sulla checkbox invece di onclick, così prende anche i click sulla label.', -15),
      (users[1], "La provo subito. Ricordati di passare il csrf_token nell'header della fetch AJAX, altrimenti Django ci blocca la POST con un errore 403.", -15),
      (users[0], "Giusto, l'ho aggiunto nello script base. Ho anche messo un po' di transizioni CSS sui badge Completed/Expired così è più fluido.", -14),
      (users[1], 'Senti, per il sistema dei permessi... come gestiamo il ruolo effettivo se uno è sia Viewer che Collaborator su rami diversi?', -10),
      (users[0], "Vince sempre il permesso più alto. Se sei Collaborator sul parent, l'algoritmo te lo propaga a cascata scavalcando eventuali restrizioni locali.", -10),
      (users[1], 'Ha senso. A proposito, occhio che se provo a eliminare questo commento mi dà errore: User.can_delete_comment() missing 1 required positional argument.', -5),
      (users[0], "Ah, me ne ero accorto! Avevo dimenticato di passare l'oggetto commento alla funzione nella view. L'ho appena fixato, fai pull.", -5),
      (users[1], 'Confermato, ora funziona alla grande. Dai che per la deadline del 22 giugno abbiamo in mano un AlmostFS perfetto.', -2)
    ]
    for user, content, days_offset in web_tech_0_comments:
      creation_date = today + datetime.timedelta(days=days_offset)
      new_comment = Comment.objects.create(project=web_technologies_0, user=user, content=content)
      Comment.objects.filter(id=new_comment.id).update(creation_date=creation_date)
    self.stdout.write("Created comments between Alessio and Christian.")

    self.stdout.write(self.style.SUCCESS('Database successfully reinitialized!'))