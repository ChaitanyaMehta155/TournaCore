"""
Unit tests for TournaCore Stage 2:
- Tournament (ABC) enforcement
- LeagueTournament implementation and method overriding
- StandingsRow creation, calculations, and tie-breaking sorting
- Polymorphic usage of Tournament references
- Prevention of double-counting team statistics
"""
import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.tournament import Tournament, LeagueTournament
from models.team import Team
from models.standing import StandingsRow


class TestTournamentABC(unittest.TestCase):
    """Tests for the abstract base class Tournament."""

    def test_tournament_cannot_be_instantiated_directly(self):
        """Verifies that Tournament is truly an abstract class with abstract methods."""
        with self.assertRaises(TypeError):
            Tournament("TOUR-1", "Abstract Cup")  # type: ignore

    def test_league_tournament_inheritance(self):
        """Verifies LeagueTournament subclasses Tournament."""
        self.assertTrue(issubclass(LeagueTournament, Tournament))
        league = LeagueTournament("L1", "Premier League")
        self.assertTrue(isinstance(league, Tournament))
        self.assertEqual(league.status, "Draft")


class TestLeagueTournament(unittest.TestCase):
    """Tests for LeagueTournament workflow and validation."""

    def setUp(self):
        self.league = LeagueTournament("L1", "Championship")
        self.team1 = Team("T1", "Team Alpha")
        self.team2 = Team("T2", "Team Beta")
        self.team3 = Team("T3", "Team Gamma")

    def test_team_registration(self):
        self.league.register_team(self.team1)
        self.league.register_team(self.team2)
        self.assertEqual(len(self.league.teams), 2)

        # Duplicate team registration should raise ValueError
        with self.assertRaises(ValueError):
            self.league.register_team(self.team1)

    def test_insufficient_teams_cannot_generate_fixtures(self):
        # 0 teams
        with self.assertRaises(ValueError):
            self.league.generate_fixtures()

        # 1 team
        self.league.register_team(self.team1)
        with self.assertRaises(ValueError):
            self.league.generate_fixtures()

    def test_generate_fixtures_and_status(self):
        self.league.register_team(self.team1)
        self.league.register_team(self.team2)
        self.league.register_team(self.team3)

        fixtures = self.league.generate_fixtures()
        # 3 teams -> 3 matches
        self.assertEqual(len(fixtures), 3)
        self.assertEqual(self.league.status, "In Progress")

        # Cannot register more teams once fixtures are generated
        team4 = Team("T4", "Team Delta")
        with self.assertRaises(ValueError):
            self.league.register_team(team4)

        # Cannot generate fixtures twice
        with self.assertRaises(ValueError):
            self.league.generate_fixtures()

    def test_record_match_result_and_completion(self):
        self.league.register_team(self.team1)
        self.league.register_team(self.team2)
        fixtures = self.league.generate_fixtures()
        self.assertEqual(len(fixtures), 1)

        match = fixtures[0]
        self.league.record_match_result(match.match_id, home_score=2, away_score=0)

        # Since all fixtures are now played, status should update to Completed
        self.assertEqual(self.league.status, "Completed")
        self.assertTrue(match.is_played)


class TestStandingsRowAndTieBreakers(unittest.TestCase):
    """Tests for StandingsRow calculations and 5-tier tie-breaking sorting."""

    def test_standings_row_calculations(self):
        t = Team("T1", "United")
        row = StandingsRow(team=t, played=3, wins=2, draws=1, losses=0, goals_for=6, goals_against=2)

        self.assertEqual(row.points, 7)  # (2 * 3) + (1 * 1)
        self.assertEqual(row.goal_difference, 4)  # 6 - 2
        self.assertEqual(row.played, 3)

    def test_tie_breaker_1_points(self):
        """Tier 1: Higher points ranks ahead."""
        t1 = Team("T1", "Team High Pts")
        t2 = Team("T2", "Team Low Pts")
        row1 = StandingsRow(t1, played=1, wins=1, draws=0, losses=0, goals_for=1, goals_against=0)  # 3 pts
        row2 = StandingsRow(t2, played=1, wins=0, draws=1, losses=0, goals_for=1, goals_against=1)  # 1 pt

        self.assertTrue(row1 < row2)  # row1 ranks ahead of row2
        sorted_rows = sorted([row2, row1])
        self.assertEqual(sorted_rows[0].team.name, "Team High Pts")

    def test_tie_breaker_2_goal_difference(self):
        """Tier 2: Equal points, higher goal difference ranks ahead."""
        t1 = Team("T1", "Team Better GD")
        t2 = Team("T2", "Team Worse GD")
        row1 = StandingsRow(t1, played=1, wins=1, draws=0, losses=0, goals_for=4, goals_against=0)  # 3 pts, GD +4
        row2 = StandingsRow(t2, played=1, wins=1, draws=0, losses=0, goals_for=2, goals_against=1)  # 3 pts, GD +1

        self.assertTrue(row1 < row2)
        sorted_rows = sorted([row2, row1])
        self.assertEqual(sorted_rows[0].team.name, "Team Better GD")

    def test_tie_breaker_3_goals_for(self):
        """Tier 3: Equal points and GD, higher goals scored (GF) ranks ahead."""
        t1 = Team("T1", "Team High Scoring")
        t2 = Team("T2", "Team Low Scoring")
        row1 = StandingsRow(t1, played=2, wins=1, draws=0, losses=1, goals_for=5, goals_against=4)  # 3 pts, GD +1, GF 5
        row2 = StandingsRow(t2, played=2, wins=1, draws=0, losses=1, goals_for=2, goals_against=1)  # 3 pts, GD +1, GF 2

        self.assertTrue(row1 < row2)
        sorted_rows = sorted([row2, row1])
        self.assertEqual(sorted_rows[0].team.name, "Team High Scoring")

    def test_tie_breaker_4_wins(self):
        """Tier 4: Equal points, GD, GF, higher number of wins ranks ahead."""
        t1 = Team("T1", "Team More Wins")
        t2 = Team("T2", "Team Fewer Wins")
        # Both 3 points, GF 3, GA 3 (GD 0)
        # Row 1: 1 win, 0 draws, 1 loss -> 3 pts
        row1 = StandingsRow(t1, played=2, wins=1, draws=0, losses=1, goals_for=3, goals_against=3)
        # Row 2: 0 wins, 3 draws, 0 losses -> 3 pts
        row2 = StandingsRow(t2, played=3, wins=0, draws=3, losses=0, goals_for=3, goals_against=3)

        self.assertTrue(row1 < row2)
        sorted_rows = sorted([row2, row1])
        self.assertEqual(sorted_rows[0].team.name, "Team More Wins")

    def test_tie_breaker_5_alphabetical(self):
        """Tier 5: Identical stats, alphabetical team name A-Z ranks ahead."""
        t1 = Team("T1", "Arsenal")
        t2 = Team("T2", "Chelsea")
        row1 = StandingsRow(t1, played=1, wins=1, draws=0, losses=0, goals_for=2, goals_against=0)
        row2 = StandingsRow(t2, played=1, wins=1, draws=0, losses=0, goals_for=2, goals_against=0)

        self.assertTrue(row1 < row2)
        sorted_rows = sorted([row2, row1])
        self.assertEqual(sorted_rows[0].team.name, "Arsenal")
        self.assertEqual(sorted_rows[1].team.name, "Chelsea")


class TestPolymorphismAndNoDoubleCounting(unittest.TestCase):
    """Tests polymorphic tournament reference and single source of truth verification."""

    def test_polymorphic_execution(self):
        """
        Executes tournament operations through a Tournament abstract type annotation/reference,
        proving true polymorphism.
        """
        def simulate_tournament(tourn: Tournament) -> list[StandingsRow]:
            tourn.generate_fixtures()
            for m in tourn.matches:
                tourn.record_match_result(m.match_id, home_score=2, away_score=1)
            return tourn.get_standings()

        league: Tournament = LeagueTournament("P1", "Polymorphic League")
        league.register_team(Team("TA", "Team A"))
        league.register_team(Team("TB", "Team B"))

        standings = simulate_tournament(league)
        self.assertEqual(len(standings), 2)
        self.assertEqual(league.status, "Completed")

    def test_no_double_counting_of_team_statistics(self):
        """
        Verifies team stats match single source of truth when retrieved via get_standings().
        """
        league = LeagueTournament("DC1", "Single Source League")
        t1 = Team("T1", "Real Madrid")
        t2 = Team("T2", "Barcelona")
        league.register_team(t1)
        league.register_team(t2)
        fixtures = league.generate_fixtures()

        match = fixtures[0]
        # Match played: Real Madrid 3 - 1 Barcelona
        league.record_match_result(match.match_id, home_score=3, away_score=1)

        # Call get_standings multiple times
        standings_1 = league.get_standings()
        standings_2 = league.get_standings()

        # Both calls should report exactly 3 points and 3 goals for Real Madrid
        self.assertEqual(standings_1[0].points, 3)
        self.assertEqual(standings_1[0].goals_for, 3)
        self.assertEqual(standings_2[0].points, 3)
        self.assertEqual(standings_2[0].goals_for, 3)

        # Direct team check
        self.assertEqual(t1.points, 3)
        self.assertEqual(t1.goals_for, 3)
        self.assertEqual(t1.matches_played, 1)


if __name__ == "__main__":
    unittest.main()
