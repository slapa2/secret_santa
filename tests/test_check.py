import unittest

from secret_santa.check import InvalidDrawError, validate_pairs
from secret_santa.models import Person

p1 = Person(name="Person_1", phone="600000001", groups=frozenset({"group_1"}))
p2 = Person(name="Person_2", phone="600000002", groups=frozenset({"group_2"}))
p3 = Person(name="Person_3", phone="600000003", groups=frozenset({"group_3"}))
p4 = Person(name="Person_4", phone="600000004", groups=frozenset({"group_1"}))
p5 = Person(name="Person_5", phone="600000005", groups=frozenset())
p6 = Person(name="Person_6", phone="600000006", groups=frozenset())
p7 = Person(name="Person_7", phone="600000007", groups=frozenset())
p8 = Person(
    name="Person_8", phone="600000008", groups=frozenset({"group_1", "group_2}"})
)
p9 = Person(
    name="Person_9", phone="600000009", groups=frozenset({"group_3", "group_4}"})
)


class CheckTest(unittest.TestCase):

    def test_valid_pairs(self):
        persons = [p1,p2,p3]
        pairs = {p1:p2, p2:p3, p3:p1}
        validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_has_no_pair_raises(self):
        persons = [p1, p2]
        pairs = {p1: p2,}
        with self.assertRaisesRegex(InvalidDrawError, "No pair for: Person_2"):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_was_not_selected_raises(self):
        persons = [p1, p2]
        pairs = {p1: p2, p2: p3}
        with self.assertRaisesRegex(InvalidDrawError, f"Not drawn: {p1.name}"):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_was_selected_two_times_raises(self):
        persons = [p1, p2, p3]
        pairs = {p1: p3, p2: p3, p3: p1}
        with self.assertRaisesRegex(InvalidDrawError, f"Not drawn: {p2.name}"):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_selected_themselves_raises(self):
        persons = [p1, p2, p3]
        pairs = {p1: p1, p2: p3, p3: p2}
        with self.assertRaisesRegex(InvalidDrawError, f"{p1.name} drew themselves"):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_selected_person_from_their_group_raises(self):
        persons = [p1,p2,p4]
        pairs = {p1:p4, p2:p1, p4:p2}
        with self.assertRaisesRegex(InvalidDrawError, f"{p1.name} and {p4.name} are in the same group"):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_mutual_pairs_if_not_allowed_raises(self):
        persons = [p1,p2]
        pairs = {p1:p2, p2:p1}
        with self.assertRaisesRegex(InvalidDrawError, f"{p1.name} and {p2.name} are a mutual pair"):
            validate_pairs(persons, pairs, allow_mutual=False)

    def test_mutual_pairs_if_allowed(self):
        persons = [p1,p2]
        pairs = {p1:p2, p2:p1}
        validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_with_no_group_can_draw_person_with_no_group(self):
        persons = [p5, p6, p7]
        pairs = {p5:p6, p6:p7, p7:p5}
        validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_from_outside_of_the_list_draws_raises(self):
        persons = [p1, p2]
        pairs = {p1: p2, p2: p1, p3: p1}
        with self.assertRaisesRegex(InvalidDrawError, f"People not on the list: {p3.name}"):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_with_two_groups_and_person_with_one_of_them_raises(self):
        persons = [p8, p1, p5]
        pairs = {p8: p1, p1: p5, p5: p8}
        with self.assertRaisesRegex(
            InvalidDrawError, f"{p8.name} and {p1.name} are in the same group"
        ):
            validate_pairs(persons, pairs, allow_mutual=True)

    def test_person_with_many_different_groups(self):
        persons = [p8, p9, p5]
        pairs = {p8: p9, p9: p5, p5: p8}
        validate_pairs(persons, pairs, allow_mutual=True)

    # x2. Kilka grup, żadnej wspólnej → poprawnie: p8, p9, p5 w kółku.
