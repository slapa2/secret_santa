# Losowanie świąteczne — opis projektu

> Dokument roboczy. Opisuje ustalenia, decyzje i plan pracy.
> Aktualizowany na bieżąco. Na koniec pracy powstanie z niego `README.md`.

## Cel

Prosta aplikacja CLI w Pythonie do losowania świątecznego:
każda osoba z listy losuje inną osobę, dla której przygotowuje prezent.

## Zasady losowania

1. Każda osoba losuje **dokładnie jedną** osobę i jest wylosowana **dokładnie raz**.
2. Nikt nie losuje samego siebie.
3. **Grupy zabronione:** osoby z tej samej grupy nie mogą wylosować siebie nawzajem.
   - Osoba należy do **najwyżej jednej** grupy (pole może być puste = brak ograniczeń).
4. **Pary wzajemne** (A → B i jednocześnie B → A) — dozwolone domyślnie,
   można je zablokować parametrem przy uruchomieniu.
5. Wynik **nie musi** tworzyć jednego łańcucha — dopuszczalne jest kilka zamkniętych cykli
   (np. A → B → C → A oraz D → E → D).
6. Losowanie używa **seeda**: domyślnie generowanego losowo, zawsze zapisywanego w pliku wyników.
   Dzięki temu każde losowanie można odtworzyć.

## Pliki

Wszystkie pliki: **CSV**, separator `;`, kodowanie UTF-8
(odczyt jako `utf-8-sig`, żeby poprawnie obsłużyć pliki z Excela zapisane z BOM).

### Lista osób (wejście)

```csv
Imię i nazwisko;Telefon;Grupa
Anna Kowalska;600111222;Kowalscy
Piotr Kowalski;600333444;Kowalscy
Ewa Nowak;600555666;
```

- `Imię i nazwisko` — **unikalny identyfikator** osoby; duplikat = błąd pliku.
- `Telefon` — **wymagany**, przechowywany jako tekst (zachowuje `+48`, zera na początku).
  Może się powtarzać (np. jeden telefon dla pary).
- `Grupa` — opcjonalna; pusta = brak ograniczeń.
- Nazwy kolumn bez względu na wielkość liter; spacje wokół wartości są usuwane;
  puste wiersze są pomijane.

### Wyniki (wyjście)

```csv
# seed: 2840193377
# pary_wzajemne: dozwolone
Losujący;Telefon;Wylosowana osoba
Anna Kowalska;600111222;Ewa Nowak
Piotr Kowalski;600333444;Anna Kowalska
Ewa Nowak;600555666;Piotr Kowalski
```

- Linie zaczynające się od `#` to metadane losowania (seed, ustawienie par wzajemnych).
- Uwaga: plik zawiera wszystkie pary — kto go otworzy, zna wyniki.

## Interfejs CLI

```bash
# losowanie
python -m secret_santa draw lista.csv -o wyniki.csv [--no-mutual-pairs] [--seed 123]

# weryfikacja istniejących wyników
python -m secret_santa check lista.csv wyniki.csv
```

`check` weryfikuje, czy:
- każda osoba z listy losuje dokładnie raz i jest wylosowana dokładnie raz,
- nikt nie wylosował siebie,
- nikt nie wylosował osoby ze swojej grupy,
- nie ma par wzajemnych (jeśli metadane wyników mówią, że były zablokowane),
- w wynikach nie występują osoby spoza listy.

Wypisuje pierwszy znaleziony problem albo `OK`. Ta sama logika służy do testowania algorytmu.

## Decyzje techniczne

- Python 3.13, **tylko biblioteka standardowa** (`csv`, `argparse`, `random`, `dataclasses`, `unittest`).
- Kod (nazwy, identyfikatory), komunikaty błędów i CLI **po angielsku**.
- Algorytm losowania to **czysta funkcja** — nie wie nic o plikach; dostaje osoby, zwraca pary.
- Seed: `random.Random(seed)` — własna instancja generatora, nie globalny `random`.
  `draw()` dostaje gotowy generator (`rng`) jako parametr — testy podają `Random(42)`.

## Algorytm losowania

**Tasuj i sprawdzaj** (*rejection sampling*): tasujemy listę obdarowanych, łączymy w pary,
sprawdzamy reguły; powtarzamy, aż wynik będzie poprawny.

- Każdy poprawny wynik jest **równie prawdopodobny** (sprawiedliwe losowanie).
- Reguły są w jednym miejscu: `draw.py` używa `validate_pairs()` z `check.py`.
- `validate_pairs()` rzuca `InvalidDrawError` (podklasa `ValueError`) przy **pierwszym**
  naruszonym warunku; `draw` łapie tylko ten wyjątek i losuje ponownie.
- Bezpiecznik: limit prób (domyślnie 1000); po jego przekroczeniu — czytelny błąd.

**Walidacja przed losowaniem** — od razu po wczytaniu listy odrzucamy przypadki niemożliwe:
- mniej niż 2 osoby,
- grupa większa niż połowa wszystkich osób (jej członkowie nie mają komu dawać prezentów),
- dokładnie 2 osoby przy zakazie par wzajemnych.

Uwaga: jedna duża grupa (np. 8 z 20 osób) wymaga średnio setek prób, a grupa równa
połowie osób — ~185 000. Typowe listy rodzinne: kilkanaście prób.

```python
# check.py
class InvalidDrawError(ValueError): ...
def validate_pairs(people: list[Person], pairs: dict[Person, Person], allow_mutual: bool) -> None

# draw.py
def draw(people: list[Person], rng: random.Random, allow_mutual: bool) -> dict[Person, Person]
```

## Planowana struktura

```
losowanie_swiateczne/
  secret_santa/
    __main__.py    # punkt wejścia: python -m secret_santa
    models.py      # dataclass Person
    reader.py      # odczyt listy osób i wyników z CSV + walidacja
    writer.py      # zapis wyników do CSV
    draw.py        # algorytm losowania
    check.py       # weryfikacja wyników
    cli.py         # argparse, spina wszystko
  tests/
  przyklad.csv
  PROJEKT.md
```

## Sposób pracy

- Pracujemy małymi krokami; każdy krok kończy się działającym kodem i commitem.
- Dla każdego kroku: najpierw ustalamy interfejs (sygnatury, odpowiedzialność),
  potem **kod pisze autor**, Claude pomaga, gdy trzeba, a na końcu proponuje refaktor.
- Git obsługuje autor; Claude sugeruje krótkie commit message po angielsku.

## Plan

- [x] 1. Szkielet projektu, `.gitignore`, przykładowy `przyklad.csv`
- [x] 2. Model danych `Person`
- [x] 3. Odczyt listy osób z CSV + walidacja + testy (`tests/test_reader.py`)
- [x] 4. Weryfikacja wyników (`check.py`) + testy
- [x] 5. Walidacja przed losowaniem + algorytm losowania (`draw.py`) + testy
- [ ] 6. Zapis wyników do CSV (z metadanymi)
- [ ] 7. CLI: `draw` i `check`
- [ ] 8. `README.md`

## Na później

- Powiadomienia SMS: każda osoba dostaje informację, kogo wylosowała.

## Dziennik decyzji

- 2026-11-21 — Lista osób w CSV zamiast xlsx → brak zewnętrznych zależności.
- 2026-11-21 — Seed losowy, zapisywany w metadanych pliku wyników.
- 2026-11-22 — CLI po angielsku: `draw`, `check`, `--no-mutual-pairs`.
- 2026-11-22 — Algorytm „tasuj i sprawdzaj” + walidacja przypadków niemożliwych przed losowaniem.
- 2026-11-22 — Najpierw `check.py`, potem `draw.py` — reguły w jednym miejscu.
- 2026-11-22 — `validate_pairs` rzuca własny wyjątek `InvalidDrawError` przy pierwszym błędzie
  (zamiast zwracać listę problemów) — spójnie z `reader.py`.
- 2026-11-22 — Komunikaty błędów po angielsku (testy sprawdzają ich treść).
- 2026-11-22 — Testy w `unittest` (bez zależności); ewentualne przejście na pytest
  nie wymaga przepisywania testów.
- 2026-11-21 — Pary wzajemne sterowane flagą `--bez-par-wzajemnych`;
  `sprawdz` odczytuje to ustawienie z metadanych wyników.
