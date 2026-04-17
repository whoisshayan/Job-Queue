from .base import JobDefinition


def sort_small_array() -> list[int]:
    numbers = [9, 3, 7, 1, 5, 2, 8, 4, 6]
    return sorted(numbers)


JOB = JobDefinition(
    code_name="sort_small_array",
    name="Sort Small Array",
    description="Sorts a short predefined array of integers and returns the sorted result.",
    execute=sort_small_array,
)
