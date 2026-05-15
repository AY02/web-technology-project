from django.contrib import admin
from .models import Document, PendingEdit


admin.site.register(Document)
admin.site.register(PendingEdit)