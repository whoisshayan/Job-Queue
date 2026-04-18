from .base import JobDefinition


def sample_job(job_execution=None) -> str:
    execution_id = getattr(job_execution, "id", "unknown")
    return f"sample_job finished successfully for execution {execution_id}."


def debug_job(job_execution=None) -> str:
    execution_id = getattr(job_execution, "id", 0)

    # Fail on even execution ids so the error path is easy to test.
    if execution_id and execution_id % 2 == 0:
        raise RuntimeError(f"debug_job failed intentionally for execution {execution_id}.")

    return f"debug_job completed successfully for execution {execution_id}."


def run_sample_job_without_execution() -> str:
    return sample_job()


def run_debug_job_without_execution() -> str:
    return debug_job()


SAMPLE_JOB = JobDefinition(
    code_name="sample_job",
    name="sample_job",
    description="Runs a simple successful sample job and returns a short text output.",
    execute=run_sample_job_without_execution,
)

DEBUG_JOB = JobDefinition(
    code_name="debug_job",
    name="debug_job",
    description="Runs a debug job that intentionally fails for some executions so failure handling can be tested.",
    execute=run_debug_job_without_execution,
)
