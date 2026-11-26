from dataclasses import dataclass


@dataclass(frozen=True)
class Person:
    name: str
    phone: str
    groups: frozenset[str] = frozenset()


@dataclass(frozen=True)
class DrawResult:
    pairs: dict[Person, Person]
    seed: int
    allow_mutual: bool
