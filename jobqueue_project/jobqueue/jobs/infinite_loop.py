import time

from .base import JobDefinition


def infinite_loop() -> None:
    while True:
        time.sleep(1)


JOB = JobDefinition(
    code_name="infinite_loop",
    name="Infinite Loop",
    description="Intentionally runs forever to simulate a stuck or timeout job.",
    execute=infinite_loop,
)
