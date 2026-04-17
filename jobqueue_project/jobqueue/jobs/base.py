from dataclasses import dataclass
from typing import Any, Callable


JobCallable = Callable[[], Any]


@dataclass(frozen=True, slots=True)
class JobDefinition:
    code_name: str
    name: str
    description: str
    execute: JobCallable

    def __post_init__(self) -> None:
        if not self.code_name:
            raise ValueError("Job code_name cannot be empty.")
        if not self.name:
            raise ValueError("Job name cannot be empty.")
        if not self.description:
            raise ValueError("Job description cannot be empty.")
        if not callable(self.execute):
            raise TypeError("Job execute must be callable.")

    def run(self) -> Any:
        return self.execute()
