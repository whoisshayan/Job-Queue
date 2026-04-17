from django.core.management.base import BaseCommand

from jobqueue.jobs.sync import sync_job_definitions_to_database


class Command(BaseCommand):
    help = "Insert or update job definitions from the registry."

    def handle(self, *args, **options):
        result = sync_job_definitions_to_database()

        self.stdout.write(
            self.style.SUCCESS(
                "Synced job definitions: "
                f"{result['created']} created, "
                f"{result['updated']} updated, "
                f"{result['total']} total."
            )
        )
