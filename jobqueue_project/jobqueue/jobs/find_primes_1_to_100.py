from .base import JobDefinition


def is_prime(number: int) -> bool:
    if number < 2:
        return False

    for divisor in range(2, int(number**0.5) + 1):
        if number % divisor == 0:
            return False

    return True


def find_primes_1_to_100() -> list[int]:
    return [number for number in range(1, 101) if is_prime(number)]


JOB = JobDefinition(
    code_name="find_primes_1_to_100",
    name="Find Prime Numbers 1 to 100",
    description="Finds all prime numbers between 1 and 100 and returns them as an array.",
    execute=find_primes_1_to_100,
)
