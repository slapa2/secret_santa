import tempfile
import unittest
from pathlib import Path

from secret_santa.writer import write_results
from secret_santa.models import Person, DrawResult

expected_content = '\n'.join([
    "# seed: 1234",
    "# allow_mutual: false",
    "Losujący;Telefon;Wylosowana osoba",
    "Person_1;600000001;Person_2",
    "Person_2;600000002;Person_3",
    "Person_3;600000003;Person_4",
    "Person_4;600000004;Person_1"
]) + "\n"

P1 = Person(name="Person_1", phone="600000001", groups=frozenset({"group_1"}))
P2 = Person(name="Person_2", phone="600000002", groups=frozenset({"group_2"}))
P3 = Person(name="Person_3", phone="600000003", groups=frozenset({"group_3"}))
P4 = Person(name="Person_4", phone="600000004", groups=frozenset({"group_1"}))

PAIRS = {
    P1: P2,
    P2: P3,
    P3: P4,
    P4: P1
}

SEED = 1234
ALLOW_MUTUAL = False


class WriteTest(unittest.TestCase):

    def test_write_results(self):
        results = DrawResult(
            pairs=PAIRS, seed=SEED, allow_mutual=ALLOW_MUTUAL
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "wyniki_test.csv"
            write_results(result=results, path=path)
            with open(path, "r", encoding='utf-8-sig', newline="") as f:
                self.assertEqual(f.read(), expected_content)

    def test_write_results_has_BOM(self):
        results = DrawResult(
            pairs=PAIRS, seed=SEED, allow_mutual=ALLOW_MUTUAL
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "wyniki_test.csv"
            write_results(result=results, path=path)
            with open(path, "r", encoding='utf-8', newline="") as f:
                self.assertEqual(f.read(), "\ufeff" + expected_content)
