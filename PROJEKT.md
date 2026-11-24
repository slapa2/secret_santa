# Losowanie świąteczne — opis projektu

> Dokument roboczy. Opisuje ustalenia, decyzje i plan pracy.
> Aktualizowany na bieżąco. Na koniec pracy powstanie z niego `README.md`.

## Cel

Prosta aplikacja CLI w Pythonie do losowania świątecznego:
każda osoba z listy losuje inną osobę, dla której przygotowuje prezent.

## Zasady losowania

1. Każda osoba losuje **dokładnie jedną** osobę i jest wylosowana **dokładnie raz**.
2. Nikt nie losuje samego siebie.
3. **Grupy zabronione:** osoby, które mają **choć jedną wspólną grupę**, nie mogą wylosować siebie nawzajem.
   - Osoba może należeć do **wielu** grup albo do żadnej (puste pole = brak ograniczeń).
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
Anna Kowalska;600111222;Kowalscy, Praca
Piotr Kowalski;600333444;Kowalscy
Ewa Nowak;600555666;
```

- `Imię i nazwisko` — **unikalny identyfikator** osoby; duplikat = błąd pliku.
- `Telefon` — **wymagany**, przechowywany jako tekst (zachowuje `+48`, zera na początku).
  Może się powtarzać (np. jeden telefon dla pary).
- `Grupa` — opcjonalna; pusta = brak ograniczeń. Kilka grup rozdziela przecinek;
  spacje wokół nazw są usuwane, puste nazwy (np. zbędny przecinek) pomijane.
- Nazwy kolumn bez względu na wielkość liter; spacje wokół wartości są usuwane;
  puste wiersze są pomijane.

### Wyniki (wyjście)

```csv
# seed: 2840193377
# allow_mutual: false
Losujący;Telefon;Wylosowana osoba
Anna Kowalska;600111222;Ewa Nowak
Piotr Kowalski;600333444;Anna Kowalska
Ewa Nowak;600555666;Piotr Kowalski
```

- Linie zaczynające się od `#` to metadane losowania (`seed`, `allow_mutual`: `true`/`false`)
  — po angielsku, czytane głównie przez program.
- Nagłówki kolumn po polsku — plik czytają ludzie.
- Końce linii `\n` w całym pliku; kodowanie `utf-8-sig` (BOM — Excel poprawnie pokaże polskie znaki).
- Kolejność wierszy = kolejność osób w pliku wejściowym.
- Uwaga: plik zawiera wszystkie pary — kto go otworzy, zna wyniki.

## Interfejs CLI

```bash
# losowanie
python -m secret_santa draw lista.csv wyniki.csv [--no-mutual-pairs] [--seed 123] [--force]

# weryfikacja istniejących wyników
python -m secret_santa check lista.csv wyniki.csv
```

`draw`:
- seed losowy (`secrets.randbelow(2**32)`), chyba że podano `--seed`; zawsze wypisywany i zapisywany w pliku,
- **odmawia nadpisania** istniejącego pliku wyników; nadpisanie tylko z `--force`.

Błędy (`ValueError` i pochodne, `TooManyAttemptsError`) — sam komunikat, bez tracebacku, kod wyjścia 1.

`check` weryfikuje, czy:
- każda osoba z listy losuje dokładnie raz i jest wylosowana dokładnie raz,
- nikt nie wylosował siebie,
- nikt nie wylosował osoby, z którą ma wspólną grupę,
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
- Bezpiecznik: limit prób (domyślnie 100 000); po jego przekroczeniu — czytelny błąd
  z informacją, że losowanie może być niemożliwe.

**Walidacja przed losowaniem** — od razu po wczytaniu listy odrzucamy przypadki niemożliwe:
- mniej niż 2 osoby,
- grupa większa niż połowa wszystkich osób (jej członkowie nie mają komu dawać prezentów),
- dokładnie 2 osoby przy zakazie par wzajemnych,
- osoba, która nie ma ani jednego dozwolonego kandydata (komunikat podaje imię).

Przy wielu grupach to nie wykrywa wszystkiego (np. dwie osoby mają tego samego jedynego
kandydata) — resztę łapie limit prób.

Uwaga: jedna duża grupa (np. 8 z 20 osób) wymaga średnio setek prób, a grupa równa
połowie osób — ~185 000. Typowe listy rodzinne: kilkanaście prób.

```python
# check.py
class InvalidDrawError(ValueError): ...
def validate_pairs(people: list[Person], pairs: dict[Person, Person], allow_mutual: bool) -> None

# draw.py
class ImpossibleDrawError(ValueError): ...
class TooManyAttemptsError(Exception): ...
def validate_feasibility(people: list[Person], allow_mutual: bool) -> None
def draw(people: list[Person], rng: random.Random, allow_mutual: bool, max_attempts: int = 100_000) -> dict[Person, Person]

# models.py
@dataclass(frozen=True)
class Person:
    name: str
    phone: str
    groups: frozenset[str] = frozenset()

@dataclass(frozen=True)
class DrawResult:
    pairs: dict[Person, Person]
    seed: int
    allow_mutual: bool

# writer.py / reader.py — ścieżka zawsze do pliku, obowiązkowa
def write_results(path: Path, result: DrawResult) -> None
def read_results(path: Path, people: list[Person]) -> DrawResult
```

Ścieżki plików pojawiają się tylko w CLI; reszta kodu dostaje gotowe dane.

## Planowana struktura

```
secret_santa/            # katalog projektu
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
- [x] 6. Zapis i odczyt wyników CSV (z metadanymi) + testy w obie strony
- [x] 7. CLI: `draw` i `check` (działa end-to-end; brak testów CLI)
- [ ] 8. Wiele grup na osobę (`Person.groups`)
- [ ] 9. `README.md`

## Na później

- Powiadomienia SMS: każda osoba dostaje informację, kogo wylosowała.

### Dług techniczny (świadomie odłożone)

- `read_results` nie wykrywa nieznanych imion ani powtórzonego losującego
  (błąd i tak wychwyci `validate_pairs`, ale z mniej precyzyjnym komunikatem).
- Brak testów błędów dla `read_results` (`ReadResultsTest` w `tests/test_reader.py`).
- `read_results` nie sprawdza nagłówka kolumn w pliku wyników.
- Brak testów integracyjnych CLI (`draw` → plik → `check`).
- Kosmetyka CLI: puste `help` dla `draw`, „override” → „overwrite” w komunikacie,
  zbędne `Path(...)` w `run_draw` (argparse już daje `Path`).

## Dziennik decyzji

- 2026-11-21 — Lista osób w CSV zamiast xlsx → brak zewnętrznych zależności.
- 2026-11-21 — Seed losowy, zapisywany w metadanych pliku wyników.
- 2026-11-22 — `draw` nie nadpisuje istniejącego pliku wyników bez `--force`
  (ochrona przed zniszczeniem losowania, które ludzie już znają).
- 2026-11-22 — `draw` przyjmuje dwa argumenty pozycyjne (lista, wyniki) — symetrycznie z `check`;
  bez `-o` i bez domyślnej nazwy pliku — użytkownik zawsze świadomie wskazuje plik wyników.
- 2026-11-22 — Wynik losowania jako `DrawResult` (pary + seed + allow_mutual); ścieżka poza nim.
- 2026-11-22 — Format wyników: metadane po angielsku (`# seed`, `# allow_mutual`), nagłówki po polsku.
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
- 2026-11-24 — Osoba może należeć do wielu grup (`groups: frozenset[str]`), w CSV po przecinku.
- 2026-11-24 — Walidacja: dodatkowo każda osoba musi mieć choć jednego dozwolonego kandydata;
  bez pełnego algorytmu skojarzeń (prostota).
- 2026-11-24 — Domyślny limit prób 100 000 zamiast 1000.
