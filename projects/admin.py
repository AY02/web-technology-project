from django.contrib import admin
from .models import Project, ProjectPermission, Comment


admin.site.register(Project)
admin.site.register(ProjectPermission)
admin.site.register(Comment)