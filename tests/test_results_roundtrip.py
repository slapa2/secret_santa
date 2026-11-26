import tempfile
import unittest
from pathlib import Path

from secret_santa.reader import read_results
from secret_santa.writer import write_results
from secret_santa.models import DrawResult, Person

CONTENT_AM_FALSE = '\n'.join([
    "# seed: 1234",
    "# allow_mutual: false",
    "Losujący;Telefon;Wylosowana osoba",
    "Person_1;600000001;Person_2",
    "Person_2;600000002;Person_3",
    "Person_3;600000003;Person_4",
    "Person_4;600000004;Person_1"
]) + "\n"

CONTENT_AM_TRUE= '\n'.join([
    "# seed: 1234",
    "# allow_mutual: true",
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

PERSONS = [P1, P2, P3, P4]

PAIRS = {
    P1: P2,
    P2: P3,
    P3: P4,
    P4: P1
}

SEED = 1234
ALLOW_MUTUAL_FALSE = False
ALLOW_MUTUAL_TRUE = True


class ResultsRoundtripTest(unittest.TestCase):

    def test_read_result_is_equal_wrote_result(self):
        results_in = DrawResult(pairs=PAIRS, seed=SEED, allow_mutual=ALLOW_MUTUAL_FALSE)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "wyniki_test.csv"
            write_results(path, results_in)

            results_out = read_results(path, PERSONS)

        self.assertEqual(results_in, results_out)


    def test_write_results_is_equal_read_results(self):

        with tempfile.TemporaryDirectory() as tmp_dir_1:
            path_1 = Path(tmp_dir_1) / "wyniki_test.csv"
            with open(path_1, "w", encoding='utf-8-sig', newline="") as f:
                f.write(CONTENT_AM_FALSE)
            results = read_results(path_1, PERSONS)

        with tempfile.TemporaryDirectory() as tmp_dir_2:
            path_2 = Path(tmp_dir_2) / "wyniki_test.csv"
            write_results(path_2, results)

            with open(path_2, "r", encoding='utf-8-sig', newline="") as f:
                self.assertEqual(f.read(), CONTENT_AM_FALSE)

    def test_read_result_is_equal_wrote_result_am_true(self):
        results_in = DrawResult(pairs=PAIRS, seed=SEED, allow_mutual=ALLOW_MUTUAL_TRUE)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "wyniki_test.csv"
            write_results(path, results_in)

            results_out = read_results(path, PERSONS)

        self.assertEqual(results_in, results_out)


    def test_write_results_is_equal_read_results_am_true(self):

        with tempfile.TemporaryDirectory() as tmp_dir_1:
            path_1 = Path(tmp_dir_1) / "wyniki_test.csv"
            with open(path_1, "w", encoding='utf-8-sig', newline="") as f:
                f.write(CONTENT_AM_TRUE)
            results = read_results(path_1, PERSONS)

        with tempfile.TemporaryDirectory() as tmp_dir_2:
            path_2 = Path(tmp_dir_2) / "wyniki_test.csv"
            write_results(path_2, results)

            with open(path_2, "r", encoding='utf-8-sig', newline="") as f:
                self.assertEqual(f.read(), CONTENT_AM_TRUE)


