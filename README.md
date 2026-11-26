# Secret Santa — losowanie świąteczne

Prosta aplikacja wiersza poleceń do świątecznego losowania: każda osoba z listy
losuje jedną inną osobę, dla której przygotowuje prezent.

- Osoby z tej samej grupy (np. rodziny, domownicy) nie losują siebie nawzajem.
- Można zablokować pary wzajemne (A → B i B → A).
- Każde losowanie ma zapisany *seed*, więc da się je odtworzyć.
- Wyniki można później zweryfikować poleceniem `check`.
- Tylko biblioteka standardowa Pythona — nic nie trzeba instalować.

## Wymagania

Python 3.13 lub nowszy.

## Szybki start

```bash
python3 -m secret_santa draw example.csv wyniki.csv
python3 -m secret_santa check example.csv wyniki.csv
```

## Lista osób

Plik CSV, separator `;`, kodowanie UTF-8 (pliki z Excela zapisane jako
„CSV UTF-8” też działają). Przykład: [`example.csv`](example.csv).

```csv
Imię i nazwisko;Telefon;Grupy
Anna Kowalska;600111222;Kowalscy
Zosia Kowalska;600777888;Kowalscy,Praca
Marek Wiśniewski;601222333;Praca
Kasia Zielińska;601444555;
```

| Kolumna | Opis |
|---|---|
| `Imię i nazwisko` | Wymagane, **unikalne** — identyfikuje osobę. |
| `Telefon` | Wymagany; może się powtarzać (np. jeden telefon dla pary). |
| `Grupy` | Kolumna wymagana, wartość opcjonalna. Kilka grup oddziel przecinkiem. Puste pole = brak ograniczeń. |

- Wielkość liter w nagłówkach i nazwach grup nie ma znaczenia (`Praca` = `praca`).
- Spacje wokół wartości są usuwane, puste wiersze pomijane.
- Osoby, które mają **choć jedną wspólną grupę**, nie mogą wylosować siebie nawzajem.

## Losowanie: `draw`

```bash
python3 -m secret_santa draw LISTA WYNIKI [opcje]
```

| Opcja | Znaczenie |
|---|---|
| `-n`, `--no-mutual-pairs` | Zakaz par wzajemnych (A → B i B → A). |
| `-s`, `--seed SEED` | Własny seed — ta sama lista i ten sam seed dają ten sam wynik. |
| `--max-attempts N` | Limit prób losowania (domyślnie 100 000). |
| `-f`, `--force` | Nadpisz istniejący plik wyników. |

Bez `--force` program **odmawia nadpisania** pliku wyników — chroni losowanie,
które ktoś mógł już zobaczyć.

Przykład:

```console
$ python3 -m secret_santa draw example.csv wyniki.csv --seed 42
Drew 7 people, seed: 42 → wyniki.csv
```

## Plik wyników

```csv
# seed: 42
# allow_mutual: true
Losujący;Telefon;Wylosowana osoba
Anna Kowalska;600111222;Ewa Nowak
Piotr Kowalski;600333444;Marek Wiśniewski
...
```

Linie z `#` to metadane losowania. Plik otwiera się poprawnie w Excelu.

> **Uwaga:** plik wyników zawiera wszystkie pary — kto go otworzy, zna wyniki.
> Repozytorium ignoruje pliki `*.csv` (poza `example.csv`), żeby wyniki
> nie trafiły przypadkiem do gita.

## Weryfikacja: `check`

```bash
python3 -m secret_santa check LISTA WYNIKI
```

Sprawdza, czy każdy losuje i jest wylosowany dokładnie raz, nikt nie wylosował
siebie ani osoby ze wspólnej grupy, nie ma par wzajemnych (jeśli były zablokowane)
i nie ma osób spoza listy. Wypisuje `result file is valid` albo pierwszy znaleziony problem.

## Kiedy losowanie jest niemożliwe

Przed losowaniem program odrzuca przypadki, które na pewno się nie udadzą:

- mniej niż 2 osoby (albo mniej niż 3 przy zakazie par wzajemnych),
- grupa liczniejsza niż połowa wszystkich osób,
- osoba, która nie ma żadnego dozwolonego kandydata.

Przy wielu grupach na osobę niektóre niemożliwe układy wychodzą dopiero w trakcie
losowania — wtedy po wyczerpaniu limitu prób pojawia się komunikat, że losowanie
może być niemożliwe. Pomaga zmniejszenie liczby grup lub dodanie osób.

Błędy są wypisywane jako krótki komunikat (`Error: ...`), kod wyjścia 1.

## Jak to działa

Algorytm „tasuj i sprawdzaj”: lista obdarowanych jest tasowana i łączona w pary,
a wynik sprawdzany tymi samymi regułami co w `check`. Jeśli coś się nie zgadza,
losowanie jest powtarzane. Dzięki temu każdy poprawny wynik jest równie prawdopodobny.

## Testy

```bash
python3 -m unittest
```

## Struktura

```
secret_santa/
  __main__.py   # punkt wejścia: python3 -m secret_santa
  cli.py        # argumenty wiersza poleceń
  models.py     # Person, DrawResult
  reader.py     # odczyt listy osób i wyników
  writer.py     # zapis wyników
  draw.py       # walidacja i algorytm losowania
  check.py      # reguły poprawności wyniku
tests/
example.csv
PROJEKT.md      # notatki projektowe i dziennik decyzji
```
