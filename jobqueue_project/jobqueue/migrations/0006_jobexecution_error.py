from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobqueue", "0005_jobexecution_snapshots"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobexecution",
            name="error",
            field=models.TextField(blank=True, default=""),
        ),
    ]
