import random
from collections import Counter

from .models import Person
from .check import validate_pairs, InvalidDrawError


class ImpossibleDrawError(ValueError):
    pass


class TooManyAttemptsError(Exception):
    pass


def validate_feasibility(people: list[Person], allow_mutual: bool) -> None:
    # 1. min length of people list = 2
    if len(people) < 2:
        raise ImpossibleDrawError("People list should have at least 2 people")

    # 2. not allow_mutual, false and length of list = 2
    if not allow_mutual and len(people) < 3:
        raise ImpossibleDrawError("When mutual pairs are forbidden list should have at least 3 people")

    # 3. some group is greater than half of people list
    group_counter = Counter()
    for person in people:
        for group in person.groups:
            group_counter[group] += 1
    if group_counter:
        greatest_group, greatest_group_size = group_counter.most_common(1)[0]
        if greatest_group_size > len(people) / 2:
            raise ImpossibleDrawError(
                f"Greatest group: {greatest_group} is greater than half of all people"
            )


def draw(people: list[Person], rng: random.Random, allow_mutual: bool, max_attempts: int = 1000) -> dict[Person, Person]:
    validate_feasibility(people, allow_mutual)

    people_copy = people.copy()

    for _ in range(max_attempts):
        rng.shuffle(people_copy)
        pairs = dict(zip(people, people_copy))
        try:
            validate_pairs(people, pairs, allow_mutual)
            return pairs
        except InvalidDrawError:
            continue

    raise TooManyAttemptsError(f"Max attempts: {max_attempts} was reached")

