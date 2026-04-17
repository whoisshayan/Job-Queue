from .base import JobDefinition


def sum_1_to_1000() -> int:
    return sum(range(1, 1001))


JOB = JobDefinition(
    code_name="sum_1_to_1000",
    name="Sum Numbers 1 to 1000",
    description="Calculates the sum of integers from 1 to 1000.",
    execute=sum_1_to_1000,
)
