from .models import Person


class InvalidDrawError(ValueError):
    """The pairs do not meet the draw rules"""


def validate_pairs(people: list[Person], pairs: dict[Person, Person], allow_mutual: bool) -> None:

    people_set = set(people)

    # 1. each person from people has exactly one pair
    without_pair = people_set - pairs.keys()
    if without_pair:
        raise InvalidDrawError(f"No pair for: {', '.join(sorted(wp.name for wp in without_pair))}")

    outsiders = pairs.keys() - people_set
    if outsiders:
        raise InvalidDrawError(f"People not on the list: {', '.join(sorted(o.name for o in outsiders))}")

    # 2. Each person from the list was selected exactly one time
    # with rule 1 holding, equal sets mean everyone was drawn exactly once.
    not_drawn = people_set - set(pairs.values())
    if not_drawn:
        raise InvalidDrawError(f"Not drawn: {', '.join(sorted(p.name for p in not_drawn))}")

    # 3. No one can select themselves.
    for giver, receiver in pairs.items():
        if giver == receiver:
            raise InvalidDrawError(f"{giver.name} drew themselves")

    # 4. No one selected person from their groups
    for giver, receiver in pairs.items():
        if not giver.groups.isdisjoint(receiver.groups):
            raise InvalidDrawError(f"{giver.name} and {receiver.name} are in the same group")

    # 5. If not allow mutual no A<->B pairs
    if not allow_mutual:
        for giver, receiver in pairs.items():
            if (receiver, giver) in pairs.items():
                raise InvalidDrawError(f"{giver.name} and {receiver.name} are a mutual pair")
