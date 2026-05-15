from django.contrib import admin
from .models import ToDoList, ToDoEntry


admin.site.register(ToDoList)
admin.site.register(ToDoEntry)