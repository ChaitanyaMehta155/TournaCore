"""
Team entity for TournaCore.
Demonstrates:
- Multiple inheritance (Team inherits from Identifiable and StatsTracker)
- Constructors calling multiple base constructors
- Encapsulation (protected roster list)
- Operator overloading (__len__, __str__, __repr__)
- Class methods (from_dict)
"""
from models.base import Identifiable, StatsTracker
from models.player import Player


class Team(Identifiable, StatsTracker):
    """
    Represents a tournament team.
    Inherits unique identification from Identifiable,
    and performance tracking from StatsTracker (Multiple Inheritance).
    """

    def __init__(self, team_id: str, name: str):
        # Explicitly initialize both base classes
        Identifiable.__init__(self, identifier=team_id)
        StatsTracker.__init__(self)

        if not name or not str(name).strip():
            raise ValueError("Team name cannot be empty.")
        self.name = str(name).strip()

        # Encapsulated roster list
        self._roster: list[Player] = []

    @property
    def team_id(self) -> str:
        """Alias for id inherited from Identifiable."""
        return self.id

    @property
    def roster(self) -> list[Player]:
        """Returns a copy of the current roster to protect internal list."""
        return list(self._roster)

    def add_player(self, player: Player):
        """
        Adds a player to the team roster.
        Validates type and checks for duplicate player IDs.
        """
        if not isinstance(player, Player):
            raise TypeError("Expected an instance of Player.")

        if self.find_player(player.player_id) is not None:
            raise ValueError(
                f"Player with ID '{player.player_id}' is already on team '{self.name}'."
            )

        self._roster.append(player)

    def remove_player(self, player_id: str) -> Player:
        """
        Removes a player from the roster by player ID.
        Returns the removed player if successful, raises ValueError if not found.
        """
        target = self.find_player(player_id)
        if target is None:
            raise ValueError(f"Player with ID '{player_id}' not found in team '{self.name}'.")

        self._roster.remove(target)
        return target

    def find_player(self, player_id: str) -> Player | None:
        """Finds a player by player_id, returning None if not found."""
        for player in self._roster:
            if player.player_id == player_id:
                return player
        return None

    def get_player_count(self) -> int:
        """Returns the number of players on the roster."""
        return len(self._roster)

    def __len__(self) -> int:
        """
        Operator overloading: len(team) returns roster size.
        """
        return len(self._roster)

    def to_dict(self) -> dict:
        """Serializes team and its roster to a dictionary."""
        return {
            "team_id": self.id,
            "name": self.name,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "roster": [player.to_dict() for player in self._roster],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        """
        Class method factory to construct a Team from a dictionary.
        Also restores players and saved statistics.
        """
        team = cls(team_id=data["team_id"], name=data["name"])
        team.matches_played = int(data.get("matches_played", 0))
        team.wins = int(data.get("wins", 0))
        team.draws = int(data.get("draws", 0))
        team.losses = int(data.get("losses", 0))
        team.goals_for = int(data.get("goals_for", 0))
        team.goals_against = int(data.get("goals_against", 0))

        # Restore roster
        for player_data in data.get("roster", []):
            team.add_player(Player.from_dict(player_data))

        return team

    def __str__(self) -> str:
        return f"Team '{self.name}' [ID: {self.id}] - Players: {len(self)} | P: {self.matches_played} W: {self.wins} D: {self.draws} L: {self.losses} Pts: {self.points}"

    def __repr__(self) -> str:
        return f"Team(team_id='{self.id}', name='{self.name}', players={len(self)})"
