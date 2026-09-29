"""
StandingsRow model for TournaCore.
Represents one team's row in the league table.
Demonstrates:
- Classes and objects
- Encapsulation
- Operator overloading (__lt__, __eq__, __gt__, __str__, __repr__)
- Deterministic tie-breaking rules
"""
from models.team import Team


class StandingsRow:
    """
    Represents the standing of a single team in a league tournament.
    Supports rich comparison (__lt__) for automated sorting.
    """

    def __init__(
        self,
        team: Team,
        played: int | None = None,
        wins: int | None = None,
        draws: int | None = None,
        losses: int | None = None,
        goals_for: int | None = None,
        goals_against: int | None = None,
    ):
        if not isinstance(team, Team):
            raise TypeError("Expected an instance of Team.")

        self.team = team

        # If explicit values are provided, use them; otherwise, pull directly
        # from the team's StatsTracker to ensure a single source of truth.
        self.played = team.matches_played if played is None else int(played)
        self.wins = team.wins if wins is None else int(wins)
        self.draws = team.draws if draws is None else int(draws)
        self.losses = team.losses if losses is None else int(losses)
        self.goals_for = team.goals_for if goals_for is None else int(goals_for)
        self.goals_against = team.goals_against if goals_against is None else int(goals_against)

        # Derived calculations
        self.goal_difference = self.goals_for - self.goals_against
        self.points = (self.wins * 3) + (self.draws * 1)

    def __lt__(self, other: "StandingsRow") -> bool:
        """
        Determines ranking priority between two teams.
        Returns True if self ranks HIGHER (ahead of) other:
        1. Points (descending - higher points ranks first)
        2. Goal difference (descending - higher GD ranks first)
        3. Goals for (descending - higher GF ranks first)
        4. Wins (descending - more wins ranks first)
        5. Team name (ascending - alphabetical order A-Z)
        """
        if not isinstance(other, StandingsRow):
            return NotImplemented

        # 1. Points descending
        if self.points != other.points:
            return self.points > other.points

        # 2. Goal difference descending
        if self.goal_difference != other.goal_difference:
            return self.goal_difference > other.goal_difference

        # 3. Goals for descending
        if self.goals_for != other.goals_for:
            return self.goals_for > other.goals_for

        # 4. Number of wins descending
        if self.wins != other.wins:
            return self.wins > other.wins

        # 5. Team name ascending (alphabetical tie-breaker)
        return self.team.name.lower() < other.team.name.lower()

    def __eq__(self, other: object) -> bool:
        """Two rows are equal if all ranking criteria match."""
        if not isinstance(other, StandingsRow):
            return False
        return (
            self.points == other.points
            and self.goal_difference == other.goal_difference
            and self.goals_for == other.goals_for
            and self.wins == other.wins
            and self.team.name.lower() == other.team.name.lower()
        )

    def __gt__(self, other: "StandingsRow") -> bool:
        if not isinstance(other, StandingsRow):
            return NotImplemented
        return not (self < other or self == other)

    def to_dict(self) -> dict:
        """Converts standing row into a dictionary representation."""
        return {
            "team_id": self.team.id,
            "team_name": self.team.name,
            "played": self.played,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "goal_difference": self.goal_difference,
            "points": self.points,
        }

    def __str__(self) -> str:
        return (
            f"{self.team.name:<16} | P: {self.played:2} | W: {self.wins:2} | "
            f"D: {self.draws:2} | L: {self.losses:2} | GF: {self.goals_for:2} | "
            f"GA: {self.goals_against:2} | GD: {self.goal_difference:+3} | Pts: {self.points:2}"
        )

    def __repr__(self) -> str:
        return (
            f"StandingsRow(team='{self.team.name}', pts={self.points}, "
            f"gd={self.goal_difference}, gf={self.goals_for})"
        )
