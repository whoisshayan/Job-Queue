from .base import JobDefinition


def division_by_zero() -> float:
    return 1 / 0


JOB = JobDefinition(
    code_name="division_by_zero",
    name="Division by Zero",
    description="Intentionally divides by zero to simulate a runtime error.",
    execute=division_by_zero,
)
