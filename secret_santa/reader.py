from pathlib import Path
import csv

from .models import Person



NAME_COLUMN = "imię i nazwisko"
PHONE_COLUMN = "telefon"
GROUP_COLUMN = "grupa"


def read_people(path: Path) -> list[Person]:
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:

        reader = csv.DictReader(f, delimiter=";")

        if reader.fieldnames is None:          # pusty plik, nie ma nawet nagłówka
            raise ValueError("File is empty")
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        missing = {NAME_COLUMN, PHONE_COLUMN, GROUP_COLUMN} - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing columns in header: {', '.join(sorted(missing))}")

        names = set()
        persons = []

        for row in reader:

            if None in row:
                raise ValueError(f"Too many columns in line {reader.line_num}")

            # strip values
            row_data = {
                k: (v.strip() or None) if v is not None else None
                for k, v in row.items()
            }

            # skip empty line
            if not any(row_data.values()):
                continue

            # name validation
            if not (name := row_data.get(NAME_COLUMN)):
                raise ValueError(f"No name in line {reader.line_num}")
            if name in names:
                raise ValueError(f"Duplicated {NAME_COLUMN} in line {reader.line_num}")
            names.add(name)

            # phone validation
            if not row_data.get(PHONE_COLUMN):
                raise ValueError(f"No phone in line {reader.line_num}")

            persons.append(
                Person(
                    name=row_data.get(NAME_COLUMN),
                    phone=row_data.get(PHONE_COLUMN),
                    group=row_data.get(GROUP_COLUMN)
                )
            )
    return persons
