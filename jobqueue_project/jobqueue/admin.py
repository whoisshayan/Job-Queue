from django.contrib import admin

from .models import JobDefinition, JobExecution


@admin.register(JobDefinition)
class JobDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "code_name", "name")
    readonly_fields = ("code_name", "name", "description")
    search_fields = ("code_name", "name", "description")


@admin.register(JobExecution)
class JobExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "job_definition", "status", "worker_id", "created_at")
    list_filter = ("status", "created_at")
    autocomplete_fields = ("job_definition",)
    list_select_related = ("job_definition",)
    ordering = ("-created_at", "-id")
    readonly_fields = (
        "job_name_snapshot",
        "job_description_snapshot",
        "created_at",
        "duration",
    )
    search_fields = (
        "job_definition__code_name",
        "job_definition__name",
        "job_definition__description",
        "job_name_snapshot",
        "job_description_snapshot",
        "worker_id",
        "result",
    )
