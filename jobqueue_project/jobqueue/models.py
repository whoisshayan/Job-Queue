from django.db import models


class PredefinedJob(models.Model):
    code_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Job(models.Model):
    class State(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"

    predefined_job = models.ForeignKey(
        PredefinedJob,
        on_delete=models.PROTECT,
        related_name="jobs",
    )
    state = models.CharField(
        max_length=10,
        choices=State.choices,
        default=State.PENDING,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.predefined_job.name} ({self.get_state_display()})"
