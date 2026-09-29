"""
Unit tests for StatsService:
- Total teams
- Total matches
- Completed matches
- Total goals
- Average goals
- Highest scoring team
- Best defensive team
- Top scoring player
- Empty tournament edge case
- Zero completed matches does not cause division by zero
- Read-only data access (does not modify state)
"""
import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.tournament import LeagueTournament
from models.team import Team
from models.player import Player
from services.stats_service import StatsService


class TestStatsService(unittest.TestCase):
    """Tests for tournament statistical calculations and edge cases."""

    def setUp(self):
        self.league = LeagueTournament("L1", "Super League")
        self.team_a = Team("TA", "Team Alpha")
        self.team_b = Team("TB", "Team Beta")
        self.team_c = Team("TC", "Team Gamma")

        # Add players
        self.p1 = Player("P1", "Player One", 25, "Forward", goals_scored=4)
        self.p2 = Player("P2", "Player Two", 24, "Midfielder", goals_scored=2)
        self.p3 = Player("P3", "Player Three", 28, "Defender", goals_scored=0)
        self.team_a.add_player(self.p1)
        self.team_a.add_player(self.p2)
        self.team_b.add_player(self.p3)

    def test_empty_tournament(self):
        """Verifies sensible default values for a completely empty tournament."""
        empty_league = LeagueTournament("EMPTY", "Empty League")
        stats = StatsService(empty_league)

        self.assertEqual(stats.get_total_teams(), 0)
        self.assertEqual(stats.get_total_matches(), 0)
        self.assertEqual(stats.get_completed_matches(), 0)
        self.assertEqual(stats.get_total_goals(), 0)
        self.assertEqual(stats.get_average_goals_per_match(), 0.0)
        self.assertIsNone(stats.get_highest_scoring_team())
        self.assertIsNone(stats.get_best_defensive_team())
        self.assertIsNone(stats.get_top_scoring_player())

        # Also verify dictionary summary
        summary = stats.get_tournament_stats()
        self.assertEqual(summary["total_teams"], 0)
        self.assertEqual(summary["total_matches"], 0)
        self.assertEqual(summary["completed_matches"], 0)
        self.assertEqual(summary["total_goals"], 0)
        self.assertEqual(summary["average_goals_per_match"], 0.0)
        self.assertIsNone(summary["highest_scoring_team"])
        self.assertIsNone(summary["best_defensive_team"])
        self.assertIsNone(summary["top_scoring_player"])

    def test_total_teams(self):
        """Calculates total registered teams."""
        stats = StatsService(self.league)
        self.assertEqual(stats.get_total_teams(), 0)

        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        self.assertEqual(stats.get_total_teams(), 2)

        self.league.register_team(self.team_c)
        self.assertEqual(stats.get_total_teams(), 3)

    def test_total_matches(self):
        """Calculates total scheduled matches before and after generation."""
        stats = StatsService(self.league)
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        self.league.register_team(self.team_c)

        # Before fixtures generated: 0
        self.assertEqual(stats.get_total_matches(), 0)

        # After fixtures generated: 3 teams -> 3 matches
        self.league.generate_fixtures()
        self.assertEqual(stats.get_total_matches(), 3)

    def test_zero_completed_matches_no_division_by_zero(self):
        """Zero completed matches returns 0.0 average without raising ZeroDivisionError."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        self.league.generate_fixtures()

        stats = StatsService(self.league)
        self.assertEqual(stats.get_completed_matches(), 0)
        self.assertEqual(stats.get_total_goals(), 0)
        self.assertEqual(stats.get_average_goals_per_match(), 0.0)
        self.assertEqual(stats.get_average_goals(), 0.0)
        self.assertIsNone(stats.get_highest_scoring_team())
        self.assertIsNone(stats.get_best_defensive_team())

    def test_completed_matches_and_total_goals(self):
        """Tracks completed matches and cumulative goals accurately."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        fixtures = self.league.generate_fixtures()
        stats = StatsService(self.league)

        self.assertEqual(len(fixtures), 1)
        match = fixtures[0]

        # Record match: Team Alpha 3 - 2 Team Beta (5 goals total)
        self.league.record_match_result(match.match_id, home_score=3, away_score=2)

        self.assertEqual(stats.get_completed_matches(), 1)
        self.assertEqual(stats.get_total_goals(), 5)
        self.assertEqual(stats.get_average_goals_per_match(), 5.0)

    def test_average_goals_multiple_matches(self):
        """Calculates rounded average goals per completed match."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        self.league.register_team(self.team_c)
        fixtures = self.league.generate_fixtures()
        stats = StatsService(self.league)

        # Match 1: 3-1 (4 goals)
        self.league.record_match_result(fixtures[0].match_id, 3, 1)
        # Match 2: 2-0 (2 goals)
        self.league.record_match_result(fixtures[1].match_id, 2, 0)

        # 6 total goals across 2 matches -> average 3.0
        self.assertEqual(stats.get_completed_matches(), 2)
        self.assertEqual(stats.get_total_goals(), 6)
        self.assertEqual(stats.get_average_goals_per_match(), 3.0)

    def test_highest_scoring_team(self):
        """Identifies the team with the highest goals_for."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        fixtures = self.league.generate_fixtures()
        match = fixtures[0]

        # Alpha 4 - 1 Beta
        self.league.record_match_result(match.match_id, 4, 1)

        stats = StatsService(self.league)
        highest = stats.get_highest_scoring_team()
        self.assertIsNotNone(highest)
        self.assertEqual(highest.name, "Team Alpha")
        self.assertEqual(highest.goals_for, 4)

    def test_best_defensive_team(self):
        """Identifies the team with the lowest goals_against."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        fixtures = self.league.generate_fixtures()
        match = fixtures[0]

        # Alpha 4 - 1 Beta
        self.league.record_match_result(match.match_id, 4, 1)

        stats = StatsService(self.league)
        best_def = stats.get_best_defensive_team()
        self.assertIsNotNone(best_def)
        # Team Alpha conceded 1 goal, Team Beta conceded 4 goals
        self.assertEqual(best_def.name, "Team Alpha")
        self.assertEqual(best_def.goals_against, 1)

    def test_top_scoring_player(self):
        """Identifies the player with the most goals scored across all rosters."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)

        stats = StatsService(self.league)
        top_player = stats.get_top_scoring_player()

        self.assertIsNotNone(top_player)
        self.assertEqual(top_player.name, "Player One")
        self.assertEqual(top_player.goals_scored, 4)

    def test_top_scoring_player_none_when_no_goals(self):
        """Returns None when players exist but none have scored any goals."""
        team = Team("T_EMPTY", "No Scorers FC")
        p = Player("P100", "Defender Dan", 22, "Defender", goals_scored=0)
        team.add_player(p)

        single_league = LeagueTournament("L_NO_GOALS", "No Goals League")
        single_league.register_team(team)

        stats = StatsService(single_league)
        self.assertIsNone(stats.get_top_scoring_player())

    def test_stats_service_read_only_integrity(self):
        """Ensures StatsService does not modify any state."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        fixtures = self.league.generate_fixtures()
        match = fixtures[0]
        self.league.record_match_result(match.match_id, 2, 1)

        stats = StatsService(self.league)

        # Snapshot
        team_a_points = self.team_a.points
        team_a_goals = self.team_a.goals_for
        match_played = match.is_played
        p1_goals = self.p1.goals_scored

        # Read all stats multiple times
        for _ in range(3):
            _ = stats.get_tournament_stats()
            _ = stats.total_teams
            _ = stats.total_matches
            _ = stats.completed_matches
            _ = stats.total_goals
            _ = stats.average_goals
            _ = stats.highest_scoring_team
            _ = stats.best_defensive_team
            _ = stats.top_scoring_player

        self.assertEqual(self.team_a.points, team_a_points)
        self.assertEqual(self.team_a.goals_for, team_a_goals)
        self.assertEqual(match.is_played, match_played)
        self.assertEqual(self.p1.goals_scored, p1_goals)

    def test_tournament_get_statistics_integration(self):
        """Verifies LeagueTournament.get_statistics() delegates to StatsService correctly."""
        self.league.register_team(self.team_a)
        self.league.register_team(self.team_b)
        fixtures = self.league.generate_fixtures()
        self.league.record_match_result(fixtures[0].match_id, 3, 0)

        stats_dict = self.league.get_statistics()
        self.assertEqual(stats_dict["total_teams"], 2)
        self.assertEqual(stats_dict["total_matches"], 1)
        self.assertEqual(stats_dict["completed_matches"], 1)
        self.assertEqual(stats_dict["total_goals"], 3)
        self.assertEqual(stats_dict["average_goals_per_match"], 3.0)
        self.assertEqual(stats_dict["highest_scoring_team"].name, "Team Alpha")
        self.assertEqual(stats_dict["best_defensive_team"].name, "Team Alpha")


if __name__ == "__main__":
    unittest.main()
