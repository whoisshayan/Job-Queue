from django.db import transaction

from jobqueue.models import PredefinedJob

from .registry import list_jobs


def sync_predefined_jobs_to_database() -> dict[str, int]:
    created_count = 0
    updated_count = 0
    job_definitions = list_jobs()

    with transaction.atomic():
        for job_definition in job_definitions:
            _, created = PredefinedJob.objects.update_or_create(
                code_name=job_definition.code_name,
                defaults={
                    "name": job_definition.name,
                    "description": job_definition.description,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

    return {
        "created": created_count,
        "updated": updated_count,
        "total": len(job_definitions),
    }
