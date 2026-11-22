import tempfile
import unittest
from pathlib import Path

from secret_santa.reader import read_people
from secret_santa.models import Person

HEADER = "Imię i nazwisko;Telefon;Grupa\n"

class ReadPeopleTest(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp_dir = Path(tmp.name)

    def read(self, content: str):
        path = self.tmp_dir / "people.csv"
        path.write_text(content, encoding="utf-8")
        return read_people(path)

    def test_reads_person(self):
        people = self.read(HEADER + "Jan Nowak;600111222;Nowak\n")
        self.assertEqual(people, [Person("Jan Nowak", "600111222", "Nowak")])

    def test_empty_group_becomes_none(self):
        people = self.read(HEADER + "Jan Nowak;600111222;\n")
        self.assertIsNone(people[0].group)

    def test_duplicated_name_raises(self):
        content = HEADER + "Anna;1;\nAnna;2;\n"
        with self.assertRaisesRegex(ValueError, "line 3"):
            self.read(content)

    def test_missing_column_raises(self):
        content = "Imię i nazwisko;Grupa\n"
        with self.assertRaisesRegex(ValueError, "telefon"):
            self.read(content)

    def test_header_ignores_case_and_spaces(self):
        header = "  Imię i nazwisko ; TELEFON ; Grupa \n"
        people = self.read(header + "Jan Nowak;600111222;Nowak\n")
        self.assertEqual(people, [Person("Jan Nowak", "600111222", "Nowak")])

    def test_strip_values(self):
        people = self.read(HEADER + " Jan Nowak ; 600111222 ; Nowak \n")
        self.assertEqual(people, [Person("Jan Nowak", "600111222", "Nowak")])

    def test_empty_file_raises(self):
        content = ""
        with self.assertRaisesRegex(ValueError, "File is empty"):
            self.read(content)

    def test_missing_name_raises(self):
        content = HEADER + ";600111222;Nowak\n"
        with self.assertRaisesRegex(ValueError, "line 2"):
            self.read(content)

    def test_missing_phone_raises(self):
        content = HEADER + "Jan Nowak;;Nowak\n"
        with self.assertRaisesRegex(ValueError, "line 2"):
            self.read(content)

    def test_too_many_columns_in_row_raises(self):
        content = HEADER + "Jan Nowak;600111222;Nowak;x\n"
        with self.assertRaisesRegex(ValueError, "line 2"):
            self.read(content)

    def test_skip_empty_line(self):
        p1 = "Jan Nowak;600111222;Nowak\n"
        p2 = "Jan Kowalski;600111223;Kowalscy\n"
        people = self.read(HEADER + p1 + "\n" + p2)
        self.assertEqual(people, [
            Person("Jan Nowak", "600111222", "Nowak"),
            Person("Jan Kowalski", "600111223", "Kowalscy")
        ])

    def test_skip_line_with_empty_columns(self):
        p1 = "Jan Nowak;600111222;Nowak\n"
        p2 = "Jan Kowalski;600111223;Kowalscy\n"
        people = self.read(HEADER + p1 + ";;\n" + ";\n" + p2)
        self.assertEqual(people, [
            Person("Jan Nowak", "600111222", "Nowak"),
            Person("Jan Kowalski", "600111223", "Kowalscy")
        ])

    def test_duplicated_phone_is_allowed(self):
        p1 = "Jan Nowak;600111222;Nowak\n"
        p2 = "Jan Kowalski;600111222;Kowalscy\n"
        people = self.read(HEADER + p1 + p2)
        self.assertEqual(people, [
            Person("Jan Nowak", "600111222", "Nowak"),
            Person("Jan Kowalski", "600111222", "Kowalscy")
        ])

    def test_header_only_returns_empty_list(self):
        people = self.read(HEADER + "\n")
        self.assertEqual(people, [])
