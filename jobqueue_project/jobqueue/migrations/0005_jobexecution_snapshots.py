from django.db import migrations, models


def populate_job_execution_snapshots(apps, schema_editor):
    JobExecution = apps.get_model("jobqueue", "JobExecution")

    for execution in JobExecution.objects.select_related("job_definition").all():
        execution.job_name_snapshot = execution.job_definition.name
        execution.job_description_snapshot = execution.job_definition.description
        execution.save(
            update_fields=[
                "job_name_snapshot",
                "job_description_snapshot",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("jobqueue", "0004_jobdefinition_jobexecution_refactor"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobexecution",
            name="job_description_snapshot",
            field=models.TextField(default="", editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="jobexecution",
            name="job_name_snapshot",
            field=models.CharField(default="", editable=False, max_length=255),
            preserve_default=False,
        ),
        migrations.RunPython(
            populate_job_execution_snapshots,
            migrations.RunPython.noop,
        ),
    ]
