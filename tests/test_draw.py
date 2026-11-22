import random
import unittest

from secret_santa.check import validate_pairs
from secret_santa.draw import ImpossibleDrawError, TooManyAttemptsError, draw, validate_feasibility
from secret_santa.models import Person

p1 = Person(name="Person_1", phone="600000001", group="group_1")
p2 = Person(name="Person_2", phone="600000002", group="group_2")
p3 = Person(name="Person_3", phone="600000003", group="group_3")
p4 = Person(name="Person_4", phone="600000004", group="group_1")
p5 = Person(name="Person_5", phone="600000005", group="group_2")
p6 = Person(name="Person_6", phone="600000006", group=None)
p7 = Person(name="Person_7", phone="600000007", group=None)
p8 = Person(name="Person_8", phone="600000008", group=None)



class NoShuffleRandom(random.Random):
    def __init__(self):
        super().__init__()
        self.shuffle_calls = 0

    def shuffle(self, x):
        self.shuffle_calls += 1


class ValidateFeasibilityTest(unittest.TestCase):

    def test_short_valid_list_allow_mutual(self):
        people = [p1, p2]
        validate_feasibility(people, allow_mutual=True)

    def test_short_valid_list_allow_mutual_false(self):
        people = [p1, p2, p3]
        validate_feasibility(people, allow_mutual=False)

    def test_too_short_list_raises(self):
        people = [p1]
        with self.assertRaisesRegex(ImpossibleDrawError, "People list should have at least 2 people"):
            validate_feasibility(people, allow_mutual=True)

    def test_allow_mutual_false_too_short_list_raises(self):
        people = [p1, p2]
        with self.assertRaisesRegex(ImpossibleDrawError, "When mutual pairs are forbidden list should have at least 3 people"):
            validate_feasibility(people, allow_mutual=False)

    def test_too_large_group_raises(self):
        people = [p1, p2, p4]
        with self.assertRaisesRegex(ImpossibleDrawError, f"Greatest group: {p1.group} is greater than half of all people"):
            validate_feasibility(people, allow_mutual=False)

    def test_people_without_group_are_not_counted_as_group(self):
        people = [p6, p7, p8, p1]
        validate_feasibility(people, allow_mutual=False)

    def test_nobody_in_group_is_feasible(self):
        people = [p6, p7, p8]
        validate_feasibility(people, allow_mutual=False)


class DrawTest(unittest.TestCase):

    def test_result_is_valid(self):
        people = [p1, p2, p3, p4, p5]
        pairs = draw(people, random.Random(42), allow_mutual=True)
        validate_pairs(people, pairs, allow_mutual=True)

    def test_same_result_with_same_seed(self):
        people = [p1, p2, p3, p4, p5]
        rng_1 = random.Random(33)
        rng_2 = random.Random(33)
        for _ in range(100):
            self.assertDictEqual(
                draw(people, rng_1, allow_mutual=True),
                draw(people, rng_2, allow_mutual=True)
            )

    def test_too_many_attempts_raises(self):
        people = [p1, p2, p3, p4, p5]
        rng = NoShuffleRandom()
        with self.assertRaises(TooManyAttemptsError):
            draw(people, rng, allow_mutual=True, max_attempts=5)
        self.assertEqual(rng.shuffle_calls, 5)
