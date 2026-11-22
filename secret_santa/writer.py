import csv
from pathlib import Path

from .models import DrawResult

GIVER_NAME_COLUMN = "Losujący"
GIVER_PHONE_COLUMN = "Telefon"
RECEIVER_NAME_COLUMN = "Wylosowana osoba"

COLUMNS = (GIVER_NAME_COLUMN, GIVER_PHONE_COLUMN, RECEIVER_NAME_COLUMN)


def write_results(path: Path, result: DrawResult) -> None:
    data = [
        {
            GIVER_NAME_COLUMN: giver.name,
            GIVER_PHONE_COLUMN: giver.phone,
            RECEIVER_NAME_COLUMN: receiver.name
        }
        for giver, receiver in result.pairs.items()
    ]

    with open(path, mode="w", encoding='utf-8-sig', newline="") as f:
        f.write(f"# seed: {result.seed}\n")
        f.write(f"# allow_mutual: {str(result.allow_mutual).lower()}\n")
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
