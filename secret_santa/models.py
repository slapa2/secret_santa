from dataclasses import dataclass


@dataclass(frozen=True)
class Person:
    name: str
    phone: str
    group: str | None = None
