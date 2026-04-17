from django.db import transaction

from jobqueue.models import JobDefinition as JobDefinitionModel

from .registry import list_jobs


def sync_job_definitions_to_database() -> dict[str, int]:
    created_count = 0
    updated_count = 0
    registry_jobs = list_jobs()

    with transaction.atomic():
        for job_definition in registry_jobs:
            _, created = JobDefinitionModel.objects.update_or_create(
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
        "total": len(registry_jobs),
    }
