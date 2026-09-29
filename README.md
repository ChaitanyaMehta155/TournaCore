# TournaCore

TournaCore is a terminal-based tournament management and ranking system implemented in Python. It provides a simple, clean, and interactive command-line interface for organizing sports leagues, generating round-robin fixture schedules, recording match results, maintaining real-time standings with deterministic tie-breaking, and computing tournament statistics.

The project is built entirely with the Python Standard Library and serves as a practical, comprehensive demonstration of Object-Oriented Programming (OOP) principles for first-year computer science students.

---

## 1. Project Overview

TournaCore allows tournament organizers, coaches, and students to manage a round-robin league tournament through a straightforward terminal interface.

Using the program, you can:
- **Create a Tournament**: Initialize a new league tournament (e.g., Premier League, Champions Trophy).
- **Add Teams**: Register competing teams into the tournament with automatic ID generation and duplicate-name prevention.
- **Add Players**: Register athletes to specific team rosters with full validation of name, age, jersey number, and position.
- **Generate Round-Robin Fixtures**: Schedule balanced matches where every team plays every other team exactly once using the circle rotation algorithm.
- **Record Match Results**: Enter final scores for scheduled matches, automatically updating team win/loss records, goal tallies, and points.
- **View League Standings**: Display an aligned, readable standings table sorted by official 5-tier ranking tie-breakers.
- **View Tournament Statistics**: Inspect tournament-wide metrics such as total goals, average goals per match, highest scoring team, best defensive team, and top scoring player.

---

## 2. Features

- **Terminal/CLI Interface**: A clean interactive menu loop (`python main.py`) driven by simple numeric options (1–9) with descriptive status banners and helpful confirmations.
- **Team Management**: Register teams into the active tournament during the draft phase, maintaining unique IDs and roster lists.
- **Player Management**: Add players to team rosters with validation for realistic ages, positions (Forward, Midfielder, Defender, Goalkeeper, Player), and unique jersey numbers per team.
- **Round-Robin Fixture Generation**: Generates balanced single round-robin fixtures using the circle/polygon rotation algorithm. Supports both even and odd team counts (using an internal BYE dummy without creating artificial matches).
- **Match Result Recording**: Record scores for unplayed matches, automatically updating matches played, wins, draws, losses, goals for, goals against, goal difference, and points on both teams without double-counting.
- **League Standings Table**: Displays an aligned terminal table showing Rank, Team Name, Played (P), Won (W), Drawn (D), Lost (L), Goals For (GF), Goals Against (GA), Goal Difference (GD), and Points (Pts).
- **5-Tier Deterministic Tie-Breaking**:
  1. Points (3 for win, 1 for draw, 0 for loss) — higher first
  2. Goal Difference ($GF - GA$) — higher first
  3. Goals For (GF) — higher first
  4. Total Wins — higher first
  5. Team Name — alphabetical order (A–Z)
- **Tournament Statistics Service**: Read-only computation of total teams, total matches, completed matches, total goals, average goals per completed match (safe against division by zero), highest scoring team, best defensive team, and top scoring player.
- **Robust Input Validation**: Graceful handling of invalid menu choices, non-numeric inputs, negative scores, unrealistic ages, duplicate team names, duplicate jerseys, and premature actions (e.g., generating fixtures with fewer than 2 teams).
- **Automated Test Suite**: 76 unit tests using Python's built-in `unittest` framework covering all models, scheduling, ranking, statistics, and CLI operations.
- **Zero External Dependencies**: Standard Library only (`sys`, `os`, `abc`, `itertools`, `unittest`).

---

## 3. OOP Concepts Demonstrated

The codebase is specifically designed to illustrate fundamental and intermediate OOP concepts naturally:

| Concept | Where it is used in TournaCore | Purpose |
|---|---|---|
| **Classes and Objects** | `Person`, `Identifiable`, `StatsTracker`, `Player`, `Team`, `Match`, `Tournament`, `LeagueTournament`, `StandingsRow`, `Scheduler`, `RankingEngine`, `StatsService`, `CLIApp` | Models domain entities, encapsulates state, and organizes modular tournament operations. |
| **Constructors (`__init__`)** | Across all classes (e.g., `Player.__init__`, `Team.__init__`, `Match.__init__`, `StandingsRow.__init__`, `CLIApp.__init__`) | Initializes entity attributes, validates initial data, and establishes baseline object state. |
| **`self` Parameter** | Used across all instance methods throughout the project | Binds methods to the current object instance, enabling access to encapsulated instance attributes. |
| **Instance Methods** | `team.add_player()`, `match.record_result()`, `tournament.register_team()`, `ranking_engine.get_rankings()`, `stats_service.get_tournament_stats()`, `cli.run()` | Encapsulates behavior and state transitions specific to an object instance. |
| **Encapsulation** | `Match._home_score`, `Match._away_score`, `Match._is_played`, `Team._roster`, `Person._age`, `Identifiable._id`, `Tournament._teams`, `Tournament._matches` | Hides sensitive internal data behind protected attributes, preventing direct external corruption. |
| **Accessor and Mutator (Properties / Getters & Setters)** | `Person.age` (`@property` and `@age.setter`), `Match.home_score`, `Match.is_played`, `Match.winner`, `Team.roster`, `StatsTracker.points`, `StatsTracker.goal_difference` | Provides controlled read access and validated write access (`age` must be an integer between 1 and 120; `team.roster` returns a defensive copy). |
| **Static Methods (`@staticmethod`)** | `Match.validate_score(score: int)` in `models/match.py`, `Scheduler.generate_round_robin_fixtures(teams)` in `services/scheduler.py` | Utility methods that perform logic without depending on instance or class state (`self` or `cls`). |
| **Class Methods (`@classmethod`)** | `Player.from_dict()`, `Team.from_dict()`, `Match.from_dict()` in `models/` | Alternative constructor/factory methods that reconstruct domain objects from dictionary representations. |
| **Single Inheritance** | `class Player(Person):` in `models/player.py`, `class LeagueTournament(Tournament):` in `models/tournament.py` | `Player` inherits personal attributes (`name`, `age`) from `Person` via `super().__init__()` and adds sports attributes; `LeagueTournament` inherits tournament management from `Tournament`. |
| **Multiple Inheritance** | `class Team(Identifiable, StatsTracker):` in `models/team.py` | `Team` inherits unique identity from `Identifiable` and performance tracking from `StatsTracker`, explicitly invoking both parent constructors. |
| **Abstract Base Class (ABC)** | `class Tournament(ABC):` in `models/tournament.py` | Defines an abstract blueprint for tournament formats that cannot be directly instantiated (`TypeError`). |
| **Abstract Methods (`@abstractmethod`)** | `@abstractmethod def generate_fixtures(self)`, `@abstractmethod def record_match_result(...)`, `@abstractmethod def get_standings(self)` in `Tournament` | Enforces that every concrete tournament subclass must implement fixture scheduling, result recording, and standings calculations. |
| **Polymorphism** | Calling `tourn.generate_fixtures()`, `tourn.record_match_result()`, and `tourn.get_standings()` on a `Tournament` reference (verified in `tests/test_tournament.py`) | Allows client code to interact with any tournament format through the common abstract `Tournament` interface. |
| **Method Overriding** | `LeagueTournament` overrides `generate_fixtures()`, `record_match_result()`, and `get_standings()`; `Player` overrides `__str__()` from `Person` | Replaces or specializes parent class methods to provide league-specific round-robin and ranking behavior. |
| **Operator Overloading** | `Team.__len__`, `StandingsRow.__lt__`, `StandingsRow.__eq__`, `StandingsRow.__gt__`, `__str__`, `__repr__` | `len(team)` returns roster size; `row1 < row2` implements the 5-tier standings tie-breaking sort; `__str__` provides readable representations. |

---

## 4. Project Structure

```text
VItyarthi project/
├── .gitignore               # Git ignore patterns for Python cache and build files
├── main.py                  # CLI application entry point (python main.py)
├── README.md                # Project documentation and evaluation guide
├── requirements.txt         # Project requirements (Standard Library only)
├── models/                  # Core domain models and abstractions
│   ├── __init__.py          # Models package export
│   ├── base.py              # Identifiable, StatsTracker, and Person classes
│   ├── match.py             # Match entity, validation, and outcome tracking
│   ├── player.py            # Player entity subclassing Person
│   ├── standing.py          # StandingsRow model with __lt__ operator overloading
│   ├── team.py              # Team entity with multiple inheritance
│   └── tournament.py        # Tournament (ABC) and LeagueTournament implementation
├── services/                # Business logic and domain services
│   ├── __init__.py          # Services package export
│   ├── ranking_engine.py    # Standings ranking service (read-only)
│   ├── scheduler.py         # Circle rotation round-robin fixture generator
│   └── stats_service.py     # Safe tournament statistics service
├── ui/                      # Terminal user interface
│   ├── __init__.py          # UI package export
│   └── menu.py              # CLIApp main menu loop and user interaction
└── tests/                   # Automated unit test suite (76 tests)
    ├── __init__.py          # Tests package marker
    ├── test_cli.py          # CLIApp interactive flow and input validation tests
    ├── test_models.py       # Base, Person, Player, Team, and Match tests
    ├── test_ranking.py      # RankingEngine and 5-tier tie-breaking tests
    ├── test_scheduler.py    # Round-robin fixture and BYE scheduling tests
    ├── test_statistics.py   # StatsService metrics and zero-division tests
    └── test_tournament.py   # Tournament ABC, LeagueTournament, and polymorphism tests
```

---

## 5. Getting Started

### Prerequisites
- Python **3.10** or higher.
- No external packages or libraries are required (`requirements.txt` specifies standard library only).

### Running the Application
From the project root directory, run:
```bash
python main.py
```

### Quick Walkthrough Demo
1. Choose **1** to create a tournament (e.g., enter `Champions League`).
2. Choose **2** to add teams (e.g., add `Real Madrid`, `Barcelona`, `Bayern Munich`).
3. Choose **3** to add a player to a team (select `1` for Real Madrid, enter `Vinicius`, `Junior`, age `23`, jersey `7`, position `Forward`).
4. Choose **4** to generate fixtures (schedules 3 round-robin matches).
5. Choose **5** to view fixtures (displays scheduled matches grouped by Round 1, 2, and 3).
6. Choose **6** to record a match result (select match `1`, enter score `3` and `1`).
7. Choose **7** to view standings (renders the updated league table with points and goal differences).
8. Choose **8** to view tournament statistics (shows total matches, goals, average goals, top team, and best defense).
9. Choose **9** to exit the application cleanly.

---

## 6. Running Tests

The test suite contains **76 automated unit tests** built using Python's standard `unittest` framework.

To execute the entire test suite from the project root:
```bash
python -m unittest discover -s tests
```

To run verbose test output:
```bash
python -m unittest discover -s tests -v
```

### Test Suite Breakdown
| Test File | Test Count | Scope |
|---|---|---|
| [`tests/test_models.py`](tests/test_models.py) | 16 tests | `Identifiable`, `StatsTracker`, `Person`, `Player`, `Team`, `Match` validation and serialization |
| [`tests/test_tournament.py`](tests/test_tournament.py) | 14 tests | `Tournament` ABC enforcement, `LeagueTournament` workflow, standings tie-breakers, polymorphism |
| [`tests/test_scheduler.py`](tests/test_scheduler.py) | 11 tests | Round-robin fixture counts ($N \times (N-1)/2$), pair uniqueness, BYE handling for odd teams |
| [`tests/test_ranking.py`](tests/test_ranking.py) | 11 tests | 5-tier standings tie-breakers, points rules (3/1/0), goal difference, statistics immutability |
| [`tests/test_statistics.py`](tests/test_statistics.py) | 12 tests | Summary metrics, empty tournaments, zero completed matches division safety, read-only integrity |
| [`tests/test_cli.py`](tests/test_cli.py) | 12 tests | `CLIApp` menu dispatch, input validation, team/player registration, fixture generation, clean exit |
| **Total** | **76 tests** | **100% passing (0 errors, 0 failures)** |
