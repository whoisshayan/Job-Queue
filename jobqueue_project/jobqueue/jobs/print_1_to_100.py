from .base import JobDefinition


def print_1_to_100() -> list[int]:
    numbers = list(range(1, 101))

    for number in numbers:
        print(number)

    return numbers


JOB = JobDefinition(
    code_name="print_1_to_100",
    name="Print Numbers 1 to 100",
    description="Prints numbers from 1 to 100 and returns them as output.",
    execute=print_1_to_100,
)
