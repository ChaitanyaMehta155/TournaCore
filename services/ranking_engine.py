"""
RankingEngine service for TournaCore.
Calculates and sorts the current standings of teams in a tournament.
Demonstrates:
- Classes and instance methods
- Read-only data access (avoids mutating team statistics)
- Sorting objects using existing StandingsRow comparison logic
"""
from models.team import Team
from models.standing import StandingsRow


class RankingEngine:
    """
    Service responsible for calculating and sorting league standings.
    Reads statistics from Team objects and produces sorted StandingsRow objects.
    """

    def create_standings(self, teams: list[Team]) -> list[StandingsRow]:
        """
        Creates StandingsRow objects for each team and returns them sorted.
        Uses StandingsRow.__lt__ for the 5-tier official tie-breaking rules:
        1. Points (descending)
        2. Goal difference (descending)
        3. Goals for (descending)
        4. Wins (descending)
        5. Team name (alphabetical order)
        """
        if not teams:
            return []

        rows: list[StandingsRow] = []
        for team in teams:
            row = StandingsRow(team=team)
            rows.append(row)

        return sorted(rows)

    def get_rankings(self, teams: list[Team]) -> list[StandingsRow]:
        """
        Returns the sorted standings rows for the provided teams.
        """
        return self.create_standings(teams)
