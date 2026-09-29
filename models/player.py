"""
Player entity for TournaCore.
Demonstrates:
- Single inheritance (Player inherits from Person)
- Constructors and super()
- Encapsulation
- Class methods (from_dict)
- Useful string representations (__str__, __repr__)
"""
from models.base import Person


class Player(Person):
    """
    Represents an athlete/player in the tournament.
    Inherits common personal attributes from Person.
    """

    VALID_POSITIONS = ["Forward", "Midfielder", "Defender", "Goalkeeper", "Player"]

    def __init__(
        self,
        player_id: str,
        name: str,
        age: int,
        position: str = "Player",
        goals_scored: int = 0,
        assists: int = 0,
    ):
        super().__init__(name=name, age=age)

        if not player_id or not str(player_id).strip():
            raise ValueError("Player ID cannot be empty.")
        self.player_id = str(player_id).strip()

        if not position or not str(position).strip():
            raise ValueError("Position cannot be empty.")
        self.position = str(position).strip().capitalize()

        if goals_scored < 0:
            raise ValueError("Goals scored cannot be negative.")
        if assists < 0:
            raise ValueError("Assists cannot be negative.")

        self._goals_scored = goals_scored
        self._assists = assists

    @property
    def goals_scored(self) -> int:
        """Accessor for goals scored."""
        return self._goals_scored

    @property
    def assists(self) -> int:
        """Accessor for assists."""
        return self._assists

    def add_goals(self, count: int = 1):
        """Increments player's goals scored."""
        if count < 0:
            raise ValueError("Cannot add negative goals.")
        self._goals_scored += count

    def add_assists(self, count: int = 1):
        """Increments player's assists count."""
        if count < 0:
            raise ValueError("Cannot add negative assists.")
        self._assists += count

    def to_dict(self) -> dict:
        """Serializes player to dictionary for JSON persistence."""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "age": self.age,
            "position": self.position,
            "goals_scored": self.goals_scored,
            "assists": self.assists,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """
        Class method factory to create a Player instance from a dictionary.
        Demonstrates class methods.
        """
        return cls(
            player_id=data["player_id"],
            name=data["name"],
            age=int(data["age"]),
            position=data.get("position", "Player"),
            goals_scored=int(data.get("goals_scored", 0)),
            assists=int(data.get("assists", 0)),
        )

    def __str__(self) -> str:
        return (
            f"[{self.player_id}] {self.name} ({self.position}, Age: {self.age}) "
            f"- Goals: {self.goals_scored}, Assists: {self.assists}"
        )

    def __repr__(self) -> str:
        return (
            f"Player(player_id='{self.player_id}', name='{self.name}', "
            f"age={self.age}, position='{self.position}')"
        )
