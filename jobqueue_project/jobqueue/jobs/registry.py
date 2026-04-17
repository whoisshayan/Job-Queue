from .base import JobDefinition
from .division_by_zero import JOB as DIVISION_BY_ZERO_JOB
from .find_primes_1_to_100 import JOB as FIND_PRIMES_1_TO_100_JOB
from .infinite_loop import JOB as INFINITE_LOOP_JOB
from .print_1_to_100 import JOB as PRINT_1_TO_100_JOB
from .sort_small_array import JOB as SORT_SMALL_ARRAY_JOB
from .sum_1_to_1000 import JOB as SUM_1_TO_1000_JOB


def build_job_registry(job_definitions: tuple[JobDefinition, ...]) -> dict[str, JobDefinition]:
    registry: dict[str, JobDefinition] = {}

    for job_definition in job_definitions:
        if job_definition.code_name in registry:
            raise ValueError(f"Duplicate job code_name: {job_definition.code_name}")

        registry[job_definition.code_name] = job_definition

    return registry


REGISTERED_JOBS = (
    PRINT_1_TO_100_JOB,
    SORT_SMALL_ARRAY_JOB,
    SUM_1_TO_1000_JOB,
    FIND_PRIMES_1_TO_100_JOB,
    DIVISION_BY_ZERO_JOB,
    INFINITE_LOOP_JOB,
)

JOB_REGISTRY = build_job_registry(REGISTERED_JOBS)


def get_job(code_name: str) -> JobDefinition:
    try:
        return JOB_REGISTRY[code_name]
    except KeyError as exc:
        raise KeyError(f"Unknown job code_name: {code_name}") from exc


def list_jobs() -> list[JobDefinition]:
    return list(JOB_REGISTRY.values())


def run_job(code_name: str):
    return get_job(code_name).run()
