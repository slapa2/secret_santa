import random
from collections import Counter

from .check import InvalidDrawError, validate_pairs
from .models import Person

DEFAULT_MAX_ATTEMPTS = 100_000


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

    # 4. person with no valid candidate
    for person in people:
        if not any(
            other.groups.isdisjoint(person.groups)
            for other in people
            if other != person
        ):
            raise ImpossibleDrawError(
                f"Person {person.name} has no valid candidate to draw"
            )


def draw(
    people: list[Person],
    rng: random.Random,
    allow_mutual: bool,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> dict[Person, Person]:
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

    raise TooManyAttemptsError(
        f"No valid draw found in {max_attempts} attempts - the draw may be impossible with these groups"
    )

