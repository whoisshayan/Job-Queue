from .base import JobDefinition
from .division_by_zero import JOB as DIVISION_BY_ZERO_JOB
from .find_primes_1_to_100 import JOB as FIND_PRIMES_1_TO_100_JOB
from .infinite_loop import JOB as INFINITE_LOOP_JOB
from .print_1_to_100 import JOB as PRINT_1_TO_100_JOB
from .sample_jobs import DEBUG_JOB, SAMPLE_JOB, debug_job, sample_job
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
    SAMPLE_JOB,
    DEBUG_JOB,
)

JOB_REGISTRY = build_job_registry(REGISTERED_JOBS)


def _wrap_zero_argument_job(job_definition: JobDefinition):
    def runner(job_execution):
        return job_definition.execute()

    return runner


JOB_CALLABLE_REGISTRY = {
    PRINT_1_TO_100_JOB.name: _wrap_zero_argument_job(PRINT_1_TO_100_JOB),
    SORT_SMALL_ARRAY_JOB.name: _wrap_zero_argument_job(SORT_SMALL_ARRAY_JOB),
    SUM_1_TO_1000_JOB.name: _wrap_zero_argument_job(SUM_1_TO_1000_JOB),
    FIND_PRIMES_1_TO_100_JOB.name: _wrap_zero_argument_job(FIND_PRIMES_1_TO_100_JOB),
    DIVISION_BY_ZERO_JOB.name: _wrap_zero_argument_job(DIVISION_BY_ZERO_JOB),
    SAMPLE_JOB.name: sample_job,
    DEBUG_JOB.name: debug_job,
}


def get_job(code_name: str) -> JobDefinition:
    try:
        return JOB_REGISTRY[code_name]
    except KeyError as exc:
        raise KeyError(f"Unknown job code_name: {code_name}") from exc


def list_jobs() -> list[JobDefinition]:
    return list(JOB_REGISTRY.values())


def get_job_callable(job_name: str):
    return JOB_CALLABLE_REGISTRY.get(job_name)


def run_job(code_name: str):
    return get_job(code_name).run()
