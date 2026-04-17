from django.db import models

# Create your models here.


class Job(models.Model):
    # Define choices for the 'state' field
    class State(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'

    # Define fields for the model
    name = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(
        max_length=10,
        choices=State.choices,  # Link the choices here
        default=State.PENDING,   # Set default value (optional)
    )

    def __str__(self):
        return self.name  # Return the 'name' field instead of 'title'