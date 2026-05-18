# web-technology-project
A simple web app for note-taking and to-do lists designed to boost students’ productivity. The web app was developed as part of the web technologies course.

---

In Django version 6.0.5, the admin cannot register models with composite primary keys. Consequently, we have implemented the ProjectPermission model with a separate identifier and have placed a constraint on the uniqueness of the (user_id, project_id) pair, even though the primary key could actually have been (user_id, project_id), as a user cannot have multiple roles on the same project.


class ProjectPermission(models.Model):
  ROLE_CHOICES = [
    ('view', 'Viewer'),
    ('comm', 'Commentator'),
    ('coll', 'Collaborator'),
  ]

  # La chiave primaria composta è stata rimossa. 
  # Django ripristinerà in automatico il classico campo 'id' autoincrementale.

  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='project_permissions'
  )
  project = models.ForeignKey(
    'Project', # Usiamo la stringa per evitare problemi di caricamento
    on_delete=models.CASCADE,
    related_name='permissions'
  )
  role = models.CharField(
    max_length=4,
    choices=ROLE_CHOICES
  )

  class Meta:
    # Ripristiniamo il vincolo di unicità: 
    # fa la stessa esatta cosa della Composite Key a livello logico!
    constraints = [
      models.UniqueConstraint(
        fields=['user', 'project'], 
        name='unique_user_project_permission'
      )
    ]

  def __str__(self):
    return f"{self.user.username} - {self.get_role_display()} on {self.project.title}"