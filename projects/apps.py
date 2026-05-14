from django.apps import AppConfig


class ProjectsConfig(AppConfig):
  name = 'projects'
  def ready(self):
    # Import the signals so that the framework can register them on
    # startup.
    import projects.signals