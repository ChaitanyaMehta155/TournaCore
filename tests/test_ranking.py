"""
Unit tests for RankingEngine and standings ranking rules:
- Win gives 3 points
- Draw gives 1 point
- Loss gives 0 points
- Goal difference is correct
- Points are the primary ranking criterion
- Goal difference is the second criterion
- Goals for is the third criterion
- Wins are the fourth criterion
- Team name is the final deterministic tie-breaker
- RankingEngine does not double-count statistics
"""
import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.team import Team
from models.standing import StandingsRow
from services.ranking_engine import RankingEngine


class TestRankingEngine(unittest.TestCase):
    """Tests for RankingEngine and the official 5-tier standings tie-breakers."""

    def setUp(self):
        self.engine = RankingEngine()

    def test_win_gives_three_points(self):
        """Win awards 3 points."""
        team = Team("T1", "Winner FC")
        team.record_match_stats(goals_scored=2, goals_conceded=1)

        standings = self.engine.get_rankings([team])
        self.assertEqual(len(standings), 1)
        self.assertEqual(standings[0].points, 3)
        self.assertEqual(standings[0].wins, 1)

    def test_draw_gives_one_point(self):
        """Draw awards 1 point."""
        team = Team("T2", "Drawer FC")
        team.record_match_stats(goals_scored=1, goals_conceded=1)

        standings = self.engine.get_rankings([team])
        self.assertEqual(len(standings), 1)
        self.assertEqual(standings[0].points, 1)
        self.assertEqual(standings[0].draws, 1)

    def test_loss_gives_zero_points(self):
        """Loss awards 0 points."""
        team = Team("T3", "Loser FC")
        team.record_match_stats(goals_scored=0, goals_conceded=2)

        standings = self.engine.get_rankings([team])
        self.assertEqual(len(standings), 1)
        self.assertEqual(standings[0].points, 0)
        self.assertEqual(standings[0].losses, 1)

    def test_goal_difference_calculation(self):
        """Goal difference is (goals_for - goals_against)."""
        t_pos = Team("T1", "Positive GD")
        t_pos.record_match_stats(5, 2)  # GD = +3

        t_neg = Team("T2", "Negative GD")
        t_neg.record_match_stats(1, 4)  # GD = -3

        t_zero = Team("T3", "Zero GD")
        t_zero.record_match_stats(2, 2)  # GD = 0

        standings = self.engine.get_rankings([t_pos, t_neg, t_zero])
        row_map = {row.team.id: row for row in standings}

        self.assertEqual(row_map["T1"].goal_difference, 3)
        self.assertEqual(row_map["T2"].goal_difference, -3)
        self.assertEqual(row_map["T3"].goal_difference, 0)

    def test_points_primary_ranking_criterion(self):
        """Criterion 1: Team with higher points ranks higher regardless of GD."""
        t_high_pts = Team("T1", "High Points")
        t_high_pts.record_match_stats(1, 0)  # 3 pts, GD +1

        t_low_pts = Team("T2", "Low Points High GD")
        t_low_pts.record_match_stats(0, 0)  # 1 pt, GD 0

        standings = self.engine.get_rankings([t_low_pts, t_high_pts])
        self.assertEqual(standings[0].team.name, "High Points")
        self.assertEqual(standings[1].team.name, "Low Points High GD")

    def test_goal_difference_second_criterion(self):
        """Criterion 2: Equal points, higher goal difference ranks first."""
        t_better_gd = Team("T1", "Better GD")
        t_better_gd.record_match_stats(4, 0)  # 3 pts, GD +4

        t_worse_gd = Team("T2", "Worse GD")
        t_worse_gd.record_match_stats(2, 1)  # 3 pts, GD +1

        standings = self.engine.get_rankings([t_worse_gd, t_better_gd])
        self.assertEqual(standings[0].team.name, "Better GD")
        self.assertEqual(standings[1].team.name, "Worse GD")

    def test_goals_for_third_criterion(self):
        """Criterion 3: Equal points and GD, higher goals scored (GF) ranks first."""
        t_more_gf = Team("T1", "High Scoring")
        t_more_gf.record_match_stats(5, 4)  # 3 pts, GD +1, GF 5

        t_fewer_gf = Team("T2", "Low Scoring")
        t_fewer_gf.record_match_stats(2, 1)  # 3 pts, GD +1, GF 2

        standings = self.engine.get_rankings([t_fewer_gf, t_more_gf])
        self.assertEqual(standings[0].team.name, "High Scoring")
        self.assertEqual(standings[1].team.name, "Low Scoring")

    def test_wins_fourth_criterion(self):
        """Criterion 4: Equal points, GD, and GF, more wins ranks first."""
        t_wins = Team("T1", "More Wins")
        t_wins.record_match_stats(3, 1)  # Win: 3 pts, GF 3, GA 1
        t_wins.record_match_stats(0, 2)  # Loss: 0 pts, GF 0, GA 2 -> Totals: 3 pts, 1 W, GF 3, GA 3, GD 0

        t_draws = Team("T2", "Fewer Wins")
        t_draws.record_match_stats(1, 1)  # Draw
        t_draws.record_match_stats(1, 1)  # Draw
        t_draws.record_match_stats(1, 1)  # Draw -> Totals: 3 pts, 0 W, GF 3, GA 3, GD 0

        standings = self.engine.get_rankings([t_draws, t_wins])
        self.assertEqual(standings[0].team.name, "More Wins")
        self.assertEqual(standings[1].team.name, "Fewer Wins")

    def test_team_name_final_deterministic_tie_breaker(self):
        """Criterion 5: All stats identical, alphabetical team name (A-Z) breaks tie."""
        t_a = Team("T1", "Arsenal")
        t_a.record_match_stats(2, 0)

        t_z = Team("T2", "Zenith")
        t_z.record_match_stats(2, 0)

        standings = self.engine.get_rankings([t_z, t_a])
        self.assertEqual(standings[0].team.name, "Arsenal")
        self.assertEqual(standings[1].team.name, "Zenith")

    def test_ranking_engine_does_not_double_count_statistics(self):
        """
        RankingEngine reads data only and does not mutate team stats
        even if called repeatedly.
        """
        team = Team("T1", "Madrid")
        team.record_match_stats(3, 1)

        # Baseline stats
        initial_points = team.points
        initial_matches = team.matches_played
        initial_gf = team.goals_for

        # Call get_rankings multiple times
        self.engine.get_rankings([team])
        self.engine.get_rankings([team])
        self.engine.create_standings([team])

        self.assertEqual(team.points, initial_points)
        self.assertEqual(team.matches_played, initial_matches)
        self.assertEqual(team.goals_for, initial_gf)

    def test_empty_teams_list(self):
        """Handling of empty teams list."""
        self.assertEqual(self.engine.get_rankings([]), [])
        self.assertEqual(self.engine.create_standings([]), [])


if __name__ == "__main__":
    unittest.main()
