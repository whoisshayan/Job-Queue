from django.contrib import admin
from .models import Job

# i am here

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "state")
    list_filter = ("state",)
    search_fields = ("name", "description")
