from django.contrib import admin

from .models import Job, PredefinedJob


@admin.register(PredefinedJob)
class PredefinedJobAdmin(admin.ModelAdmin):
    list_display = ("id", "code_name", "name")
    readonly_fields = ("code_name", "name", "description")
    search_fields = ("code_name", "name", "description")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "predefined_job", "state")
    list_filter = ("state",)
    autocomplete_fields = ("predefined_job",)
    list_select_related = ("predefined_job",)
    ordering = ("id",)
    search_fields = (
        "predefined_job__code_name",
        "predefined_job__name",
        "predefined_job__description",
    )
