from django.db import models


class JobDefinition(models.Model):
    code_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobExecution(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        TIMEOUT = "timeout", "Timeout"

    job_definition = models.ForeignKey(
        JobDefinition,
        on_delete=models.CASCADE,
        related_name="executions",
    )
    job_name_snapshot = models.CharField(max_length=255, editable=False)
    job_description_snapshot = models.TextField(editable=False)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    result = models.TextField(blank=True, default="")
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    worker_id = models.CharField(max_length=255, null=True, blank=True)
    output_file_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def populate_job_snapshot(self) -> None:
        self.job_name_snapshot = self.job_definition.name
        self.job_description_snapshot = self.job_definition.description

    def save(self, *args, **kwargs):
        if self._state.adding or not self.job_name_snapshot or not self.job_description_snapshot:
            self.populate_job_snapshot()

            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {
                    "job_name_snapshot",
                    "job_description_snapshot",
                }

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_name_snapshot} ({self.get_status_display()})"
