"""
Unit tests for Scheduler service (Round-robin fixture generation):
- 2 teams produce 1 match
- 3 teams produce 3 matches
- 4 teams produce 6 matches
- 5 teams produce 10 matches
- 6 teams produce 15 matches
- No team plays itself
- No duplicate pairings
- Every pair plays exactly once
- Odd numbers of teams handled with BYE (no dummy match created)
"""
import unittest
import sys
import os
from itertools import combinations

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.team import Team
from services.scheduler import Scheduler, generate_round_robin_fixtures


class TestScheduler(unittest.TestCase):
    """Tests for round-robin tournament fixture scheduling."""

    def _create_teams(self, count: int) -> list[Team]:
        """Helper to create N dummy teams."""
        return [Team(team_id=f"T{i}", name=f"Team {chr(65 + i)}") for i in range(count)]

    def test_two_teams_produce_one_match(self):
        """2 teams produce N*(N-1)/2 = 1 match."""
        teams = self._create_teams(2)
        fixtures = Scheduler.generate_round_robin_fixtures(teams)
        self.assertEqual(len(fixtures), 1)

    def test_three_teams_produce_three_matches(self):
        """3 teams produce N*(N-1)/2 = 3 matches."""
        teams = self._create_teams(3)
        fixtures = Scheduler.generate_round_robin_fixtures(teams)
        self.assertEqual(len(fixtures), 3)

    def test_four_teams_produce_six_matches(self):
        """4 teams produce N*(N-1)/2 = 6 matches."""
        teams = self._create_teams(4)
        fixtures = Scheduler.generate_round_robin_fixtures(teams)
        self.assertEqual(len(fixtures), 6)

    def test_five_teams_produce_ten_matches(self):
        """5 teams produce N*(N-1)/2 = 10 matches."""
        teams = self._create_teams(5)
        fixtures = Scheduler.generate_round_robin_fixtures(teams)
        self.assertEqual(len(fixtures), 10)

    def test_six_teams_produce_fifteen_matches(self):
        """6 teams produce N*(N-1)/2 = 15 matches."""
        teams = self._create_teams(6)
        fixtures = Scheduler.generate_round_robin_fixtures(teams)
        self.assertEqual(len(fixtures), 15)

    def test_no_team_plays_itself(self):
        """Ensures that home_team != away_team in every generated fixture."""
        for n in range(2, 7):
            teams = self._create_teams(n)
            fixtures = Scheduler.generate_round_robin_fixtures(teams)
            for match in fixtures:
                self.assertNotEqual(
                    match.home_team.id,
                    match.away_team.id,
                    f"Team {match.home_team.name} is scheduled to play against itself!",
                )

    def test_no_duplicate_pairings(self):
        """Ensures that no pair of teams plays each other more than once."""
        for n in range(2, 7):
            teams = self._create_teams(n)
            fixtures = Scheduler.generate_round_robin_fixtures(teams)
            seen_pairings = set()
            for match in fixtures:
                # Unordered pair representation
                pair = frozenset([match.home_team.id, match.away_team.id])
                self.assertNotIn(
                    pair,
                    seen_pairings,
                    f"Duplicate pairing found for teams {match.home_team.name} and {match.away_team.name}!",
                )
                seen_pairings.add(pair)

    def test_every_pair_plays_exactly_once(self):
        """
        Ensures all possible combinations of 2 teams are scheduled
        and played exactly once.
        """
        for n in range(2, 7):
            teams = self._create_teams(n)
            fixtures = Scheduler.generate_round_robin_fixtures(teams)

            scheduled_pairs = {
                frozenset([m.home_team.id, m.away_team.id]) for m in fixtures
            }

            expected_pairs = {
                frozenset([t1.id, t2.id]) for t1, t2 in combinations(teams, 2)
            }

            self.assertEqual(scheduled_pairs, expected_pairs)
            expected_count = n * (n - 1) // 2
            self.assertEqual(len(fixtures), expected_count)

    def test_odd_numbers_of_teams_use_bye_without_dummy_matches(self):
        """
        Ensures odd numbers of teams use BYE internally and never generate
        a match with None or dummy teams.
        """
        teams = self._create_teams(3)
        fixtures = Scheduler.generate_round_robin_fixtures(teams)
        for match in fixtures:
            self.assertIsNotNone(match.home_team)
            self.assertIsNotNone(match.away_team)
            self.assertTrue(isinstance(match.home_team, Team))
            self.assertTrue(isinstance(match.away_team, Team))

    def test_invalid_team_counts(self):
        """Requires at least 2 teams."""
        with self.assertRaises(ValueError):
            Scheduler.generate_round_robin_fixtures([])

        teams_1 = self._create_teams(1)
        with self.assertRaises(ValueError):
            Scheduler.generate_round_robin_fixtures(teams_1)

    def test_functional_wrapper(self):
        """Tests that generate_round_robin_fixtures function matches Scheduler method."""
        teams = self._create_teams(4)
        fixtures = generate_round_robin_fixtures(teams)
        self.assertEqual(len(fixtures), 6)


if __name__ == "__main__":
    unittest.main()
