from django.contrib import admin
from .models import Project


admin.site.register(Project)

# In Django version 6.0.5, the admin cannot save models with composite primary
# keys.
# admin.site.register(ProjectPermission)