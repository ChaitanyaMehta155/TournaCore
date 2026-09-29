"""
Match entity for TournaCore.
Demonstrates:
- Classes and objects
- Encapsulation (protected scores and played status)
- Static methods (validate_score)
- Class methods (from_dict)
- Properties and validation
- Operator overloading (__str__, __repr__)
"""
from models.team import Team


class Match:
    """
    Represents a single match between two teams in a tournament round.
    """

    def __init__(
        self,
        match_id: str,
        home_team: Team,
        away_team: Team,
        round_number: int,
    ):
        if not match_id or not str(match_id).strip():
            raise ValueError("Match ID cannot be empty.")
        if not isinstance(home_team, Team) or not isinstance(away_team, Team):
            raise TypeError("Both home_team and away_team must be instances of Team.")
        if home_team.id == away_team.id:
            raise ValueError("A team cannot play against itself.")
        if not isinstance(round_number, int) or round_number <= 0:
            raise ValueError("Round number must be a positive integer.")

        self.match_id = str(match_id).strip()
        self.home_team = home_team
        self.away_team = away_team
        self.round_number = round_number

        # Encapsulated state
        self._home_score: int | None = None
        self._away_score: int | None = None
        self._is_played: bool = False

    @property
    def home_score(self) -> int | None:
        """Accessor for home team's score."""
        return self._home_score

    @property
    def away_score(self) -> int | None:
        """Accessor for away team's score."""
        return self._away_score

    @property
    def is_played(self) -> bool:
        """Indicates whether this match has been concluded."""
        return self._is_played

    @staticmethod
    def validate_score(score: int) -> bool:
        """
        Static method to validate a score value.
        Demonstrates static methods: does not rely on instance or class state.
        """
        return isinstance(score, int) and score >= 0

    def record_result(self, home_score: int, away_score: int):
        """
        Records the match score, marks the match as played,
        and updates the performance statistics of both teams.
        """
        if not self.validate_score(home_score):
            raise ValueError(f"Invalid home score: {home_score}. Score must be a non-negative integer.")
        if not self.validate_score(away_score):
            raise ValueError(f"Invalid away score: {away_score}. Score must be a non-negative integer.")

        if self._is_played:
            raise ValueError(f"Match '{self.match_id}' has already been played.")

        self._home_score = home_score
        self._away_score = away_score
        self._is_played = True

        # Automatically update team statistics
        self.home_team.record_match_stats(goals_scored=home_score, goals_conceded=away_score)
        self.away_team.record_match_stats(goals_scored=away_score, goals_conceded=home_score)

    @property
    def winner(self) -> Team | None:
        """
        Returns the winning Team instance, or None if the match is drawn or unplayed.
        """
        if not self._is_played:
            return None
        if self._home_score > self._away_score:
            return self.home_team
        if self._away_score > self._home_score:
            return self.away_team
        return None  # Draw

    @property
    def is_draw(self) -> bool:
        """Returns True if the match was played and ended in a draw."""
        if not self._is_played:
            return False
        return self._home_score == self._away_score

    def to_dict(self) -> dict:
        """Serializes match to dictionary for JSON persistence."""
        return {
            "match_id": self.match_id,
            "home_team_id": self.home_team.id,
            "away_team_id": self.away_team.id,
            "round_number": self.round_number,
            "home_score": self._home_score,
            "away_score": self._away_score,
            "is_played": self._is_played,
        }

    @classmethod
    def from_dict(cls, data: dict, teams_by_id: dict[str, Team]) -> "Match":
        """
        Class method factory to reconstruct a Match using a lookup dictionary of Teams.
        Demonstrates class methods.
        """
        home_id = data["home_team_id"]
        away_id = data["away_team_id"]

        if home_id not in teams_by_id or away_id not in teams_by_id:
            raise KeyError(f"Teams {home_id} or {away_id} not found in provided lookup.")

        match = cls(
            match_id=data["match_id"],
            home_team=teams_by_id[home_id],
            away_team=teams_by_id[away_id],
            round_number=int(data["round_number"]),
        )

        if data.get("is_played", False):
            match._home_score = data["home_score"]
            match._away_score = data["away_score"]
            match._is_played = True

        return match

    def __str__(self) -> str:
        if self._is_played:
            return (
                f"[Round {self.round_number}] {self.home_team.name} {self._home_score} - "
                f"{self._away_score} {self.away_team.name} (FT)"
            )
        return f"[Round {self.round_number}] {self.home_team.name} vs {self.away_team.name} (Scheduled)"

    def __repr__(self) -> str:
        return (
            f"Match(id='{self.match_id}', round={self.round_number}, "
            f"home='{self.home_team.name}', away='{self.away_team.name}', played={self._is_played})"
        )
