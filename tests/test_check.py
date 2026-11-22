import unittest


from secret_santa.models import Person
from secret_santa.check import validate_pairs, InvalidDrawError


p1 = Person(name="Person_1", phone="600000001", group="group_1")
p2 = Person(name="Person_2", phone="600000002", group="group_2")
p3 = Person(name="Person_3", phone="600000003", group="group_3")
p4 = Person(name="Person_4", phone="600000004", group="group_1")
p5 = Person(name="Person_5", phone="600000005", group=None)
p6 = Person(name="Person_6", phone="600000006", group=None)
p7 = Person(name="Person_7", phone="600000007", group=None)




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

