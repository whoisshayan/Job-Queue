from django.core.management.base import BaseCommand

from jobqueue.jobs.sync import sync_predefined_jobs_to_database


class Command(BaseCommand):
    help = "Insert or update predefined jobs from the registry."

    def handle(self, *args, **options):
        result = sync_predefined_jobs_to_database()

        self.stdout.write(
            self.style.SUCCESS(
                "Synced predefined jobs: "
                f"{result['created']} created, "
                f"{result['updated']} updated, "
                f"{result['total']} total."
            )
        )
