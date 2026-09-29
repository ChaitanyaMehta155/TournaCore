"""
Tournament models for TournaCore.
Demonstrates:
- Abstract Base Classes (ABC) and Abstract Methods (@abstractmethod)
- Single inheritance and method overriding
- Polymorphism (working with Tournament references)
- Encapsulation of tournament state and match progress
"""
from abc import ABC, abstractmethod
from models.team import Team
from models.match import Match
from models.standing import StandingsRow
from services.scheduler import Scheduler
from services.ranking_engine import RankingEngine
from services.stats_service import StatsService


class Tournament(ABC):
    """
    Abstract Base Class defining the contract for any tournament format.
    Cannot be instantiated directly.
    """

    def __init__(self, tournament_id: str, name: str):
        if not tournament_id or not str(tournament_id).strip():
            raise ValueError("Tournament ID cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Tournament name cannot be empty.")

        self.tournament_id = str(tournament_id).strip()
        self.name = str(name).strip()
        self._teams: list[Team] = []
        self._matches: list[Match] = []
        self.status = "Draft"  # Statuses: Draft, In Progress, Completed

    @property
    def teams(self) -> list[Team]:
        """Returns a copy of registered teams."""
        return list(self._teams)

    @property
    def matches(self) -> list[Match]:
        """Returns a copy of tournament matches."""
        return list(self._matches)

    def register_team(self, team: Team):
        """
        Registers a team into the tournament before fixtures are generated.
        """
        if not isinstance(team, Team):
            raise TypeError("Expected an instance of Team.")

        if self.status != "Draft":
            raise ValueError("Cannot register teams after fixtures have been generated.")

        if self.find_team(team.id) is not None:
            raise ValueError(f"Team with ID '{team.id}' is already registered in '{self.name}'.")

        self._teams.append(team)

    def find_team(self, team_id: str) -> Team | None:
        """Finds a team by team_id."""
        for team in self._teams:
            if team.id == team_id:
                return team
        return None

    def find_match(self, match_id: str) -> Match | None:
        """Finds a match by match_id."""
        for match in self._matches:
            if match.match_id == match_id:
                return match
        return None

    def get_completed_matches(self) -> list[Match]:
        """Returns all matches that have been played."""
        return [m for m in self._matches if m.is_played]

    def get_upcoming_matches(self) -> list[Match]:
        """Returns all matches yet to be played."""
        return [m for m in self._matches if not m.is_played]

    @abstractmethod
    def generate_fixtures(self) -> list[Match]:
        """Abstract method to create tournament schedule."""
        pass

    @abstractmethod
    def record_match_result(self, match_id: str, home_score: int, away_score: int):
        """Abstract method to record score for a scheduled match."""
        pass

    @abstractmethod
    def get_standings(self) -> list[StandingsRow]:
        """Abstract method to calculate and return current standings."""
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__} '{self.name}' [ID: {self.tournament_id}, Status: {self.status}]"


class LeagueTournament(Tournament):
    """
    Concrete implementation of a Single-Division Round-Robin League.
    Overrides abstract methods from Tournament.
    """

    def __init__(self, tournament_id: str, name: str):
        super().__init__(tournament_id=tournament_id, name=name)
        self._ranking_engine = RankingEngine()
        self._stats_service = StatsService(self)

    def generate_fixtures(self) -> list[Match]:
        """
        Overrides abstract method.
        Generates single round-robin fixtures using the Scheduler service.
        """
        if len(self._teams) < 2:
            raise ValueError("At least 2 teams are required to generate fixtures.")

        if self._matches:
            raise ValueError("Fixtures have already been generated for this tournament.")

        # Delegate scheduling to the Scheduler service
        self._matches = Scheduler.generate_round_robin_fixtures(self._teams)
        self.status = "In Progress"
        return list(self._matches)

    def record_match_result(self, match_id: str, home_score: int, away_score: int):
        """
        Overrides abstract method.
        Locates the match and records the scores.
        Note: match.record_result() automatically updates each team's StatsTracker.
        """
        match = self.find_match(match_id)
        if match is None:
            raise ValueError(f"Match with ID '{match_id}' not found.")

        # Record result (updates Match and Team stats)
        match.record_result(home_score=home_score, away_score=away_score)

        # Update tournament status if all fixtures have finished
        if self._matches and all(m.is_played for m in self._matches):
            self.status = "Completed"

    def get_standings(self) -> list[StandingsRow]:
        """
        Overrides abstract method.
        Delegates ranking calculation to RankingEngine service.
        Returns rows sorted according to official ranking rules.
        """
        return self._ranking_engine.get_rankings(self._teams)

    def get_statistics(self) -> dict:
        """
        Calculates and returns tournament statistics using StatsService.
        """
        return self._stats_service.get_tournament_stats()

