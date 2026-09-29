"""
Base classes and mixins for TournaCore entities.
Demonstrates:
- Classes and objects
- Constructors
- Encapsulation (protected attributes and property getters/setters)
- Static validation concepts
"""


class Identifiable:
    """
    Base class providing a unique identifier.
    Used for entities that need a persistent ID.
    """

    def __init__(self, identifier: str):
        if not identifier or not str(identifier).strip():
            raise ValueError("ID cannot be empty or whitespace.")
        self._id = str(identifier).strip()

    @property
    def id(self) -> str:
        """Accessor for the unique identifier."""
        return self._id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self._id}')"


class StatsTracker:
    """
    Tracks match performance statistics (matches, results, goals).
    Designed to be inherited by teams or standings rows.
    """

    def __init__(self):
        self.matches_played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0

    def record_match_stats(self, goals_scored: int, goals_conceded: int):
        """
        Updates match statistics based on goals scored and conceded.
        """
        if goals_scored < 0 or goals_conceded < 0:
            raise ValueError("Goals cannot be negative.")

        self.matches_played += 1
        self.goals_for += goals_scored
        self.goals_against += goals_conceded

        if goals_scored > goals_conceded:
            self.wins += 1
        elif goals_scored == goals_conceded:
            self.draws += 1
        else:
            self.losses += 1

    def reset_stats(self):
        """Resets all tracked statistics back to zero."""
        self.matches_played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0

    @property
    def points(self) -> int:
        """
        Calculates tournament points:
        Win = 3 points, Draw = 1 point, Loss = 0 points.
        """
        return (self.wins * 3) + (self.draws * 1)

    @property
    def goal_difference(self) -> int:
        """Calculates goal difference (goals scored - goals conceded)."""
        return self.goals_for - self.goals_against


class Person:
    """
    Represents a general person.
    Demonstrates encapsulation and property setters with validation.
    """

    def __init__(self, name: str, age: int):
        if not name or not str(name).strip():
            raise ValueError("Name cannot be empty.")
        self.name = str(name).strip()
        self._age = 0
        self.age = age  # Uses setter for validation

    @property
    def age(self) -> int:
        """Accessor for age."""
        return self._age

    @age.setter
    def age(self, value: int):
        """Mutator for age with validation."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Age must be a positive integer.")
        if value > 120:
            raise ValueError("Age must be realistic (less than 120).")
        self._age = value

    def display_info(self) -> str:
        """Returns a string description of the person."""
        return f"{self.name} (Age: {self.age})"

    def __str__(self) -> str:
        return self.display_info()
