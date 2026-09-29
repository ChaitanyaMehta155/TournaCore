"""
StatsService for TournaCore.
Provides tournament performance metrics and summary statistics.
Demonstrates:
- Read-only data inspection
- Safe arithmetic (division by zero prevention)
- Handling empty/unplayed tournament edge cases
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.tournament import Tournament
from models.team import Team
from models.player import Player



class StatsService:
    """
    Calculates statistical insights for tournaments.
    Only reads existing data and never modifies tournament, team, or player state.
    """

    def __init__(self, tournament: Tournament | None = None):
        self._tournament = tournament

    def _resolve_tournament(self, tournament: Tournament | None = None) -> Tournament | None:
        """Helper to get tournament passed either via method call or constructor."""
        if tournament is not None:
            return tournament
        return self._tournament

    def get_total_teams(self, tournament: Tournament | None = None) -> int:
        """Returns the total number of registered teams."""
        t = self._resolve_tournament(tournament)
        if t is None:
            return 0
        return len(t.teams)

    def get_total_matches(self, tournament: Tournament | None = None) -> int:
        """Returns the total number of scheduled matches."""
        t = self._resolve_tournament(tournament)
        if t is None:
            return 0
        return len(t.matches)

    def get_completed_matches(self, tournament: Tournament | None = None) -> int:
        """Returns the number of finished matches."""
        t = self._resolve_tournament(tournament)
        if t is None:
            return 0
        return len(t.get_completed_matches())

    def get_total_goals(self, tournament: Tournament | None = None) -> int:
        """Returns the total goals scored across all completed matches."""
        t = self._resolve_tournament(tournament)
        if t is None:
            return 0

        total = 0
        for match in t.matches:
            if match.is_played:
                home_score = match.home_score if match.home_score is not None else 0
                away_score = match.away_score if match.away_score is not None else 0
                total += home_score + away_score
        return total

    def get_average_goals_per_match(self, tournament: Tournament | None = None) -> float:
        """
        Returns average goals per completed match.
        Avoids division by zero when no matches have been completed.
        """
        t = self._resolve_tournament(tournament)
        completed = self.get_completed_matches(t)
        if completed == 0:
            return 0.0

        total_goals = self.get_total_goals(t)
        return round(total_goals / completed, 2)

    def get_average_goals(self, tournament: Tournament | None = None) -> float:
        """Convenience alias for get_average_goals_per_match."""
        return self.get_average_goals_per_match(tournament)

    def get_highest_scoring_team(self, tournament: Tournament | None = None) -> Team | None:
        """
        Returns the team with the most goals scored (goals_for).
        Returns None if tournament is empty or no matches have been completed.
        """
        t = self._resolve_tournament(tournament)
        if t is None or not t.teams:
            return None

        # If no matches have been completed and no team has scored
        if self.get_completed_matches(t) == 0 and all(team.goals_for == 0 for team in t.teams):
            return None

        highest_team = t.teams[0]
        for team in t.teams[1:]:
            if team.goals_for > highest_team.goals_for:
                highest_team = team
        return highest_team

    def get_best_defensive_team(self, tournament: Tournament | None = None) -> Team | None:
        """
        Returns the team with the fewest goals conceded (goals_against).
        Returns None if tournament is empty or no matches have been completed.
        """
        t = self._resolve_tournament(tournament)
        if t is None or not t.teams:
            return None

        # If no matches have been completed and no team has played
        if self.get_completed_matches(t) == 0 and all(team.matches_played == 0 for team in t.teams):
            return None

        best_team = t.teams[0]
        for team in t.teams[1:]:
            if team.goals_against < best_team.goals_against:
                best_team = team
        return best_team

    def get_top_scoring_player(self, tournament: Tournament | None = None) -> Player | None:
        """
        Returns the player with the highest goals scored across all team rosters.
        Returns None if no players exist or no player has scored any goals.
        """
        t = self._resolve_tournament(tournament)
        if t is None or not t.teams:
            return None

        all_players: list[Player] = []
        for team in t.teams:
            for player in team.roster:
                all_players.append(player)

        if not all_players:
            return None

        # If all players have 0 goals scored
        if all(player.goals_scored == 0 for player in all_players):
            return None

        top_player = all_players[0]
        for player in all_players[1:]:
            if player.goals_scored > top_player.goals_scored:
                top_player = player
        return top_player

    def get_tournament_stats(self, tournament: Tournament | None = None) -> dict:
        """
        Compiles and returns a summary dictionary of tournament statistics.
        """
        t = self._resolve_tournament(tournament)
        return {
            "total_teams": self.get_total_teams(t),
            "total_matches": self.get_total_matches(t),
            "completed_matches": self.get_completed_matches(t),
            "total_goals": self.get_total_goals(t),
            "average_goals_per_match": self.get_average_goals_per_match(t),
            "highest_scoring_team": self.get_highest_scoring_team(t),
            "best_defensive_team": self.get_best_defensive_team(t),
            "top_scoring_player": self.get_top_scoring_player(t),
        }

    def get_summary(self, tournament: Tournament | None = None) -> dict:
        """Convenience alias for get_tournament_stats."""
        return self.get_tournament_stats(tournament)

    # Property accessors for convenient object-oriented usage
    @property
    def total_teams(self) -> int:
        return self.get_total_teams()

    @property
    def total_matches(self) -> int:
        return self.get_total_matches()

    @property
    def completed_matches(self) -> int:
        return self.get_completed_matches()

    @property
    def total_goals(self) -> int:
        return self.get_total_goals()

    @property
    def average_goals(self) -> float:
        return self.get_average_goals_per_match()

    @property
    def highest_scoring_team(self) -> Team | None:
        return self.get_highest_scoring_team()

    @property
    def best_defensive_team(self) -> Team | None:
        return self.get_best_defensive_team()

    @property
    def top_scoring_player(self) -> Player | None:
        return self.get_top_scoring_player()
