"""
Unit tests for TournaCore Stage 1 Models:
- Identifiable, StatsTracker, Person
- Player (Single inheritance)
- Team (Multiple inheritance)
- Match (Encapsulation, static method, operator overloading)
"""
import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.base import Identifiable, StatsTracker, Person
from models.player import Player
from models.team import Team
from models.match import Match


class TestBaseModels(unittest.TestCase):
    """Tests for base abstractions: Identifiable, StatsTracker, and Person."""

    def test_identifiable_valid_and_empty(self):
        ident = Identifiable("ID-101")
        self.assertEqual(ident.id, "ID-101")

        with self.assertRaises(ValueError):
            Identifiable("")
        with self.assertRaises(ValueError):
            Identifiable("   ")

    def test_stats_tracker_workflow(self):
        tracker = StatsTracker()
        self.assertEqual(tracker.matches_played, 0)
        self.assertEqual(tracker.points, 0)

        # Win: 3-1
        tracker.record_match_stats(goals_scored=3, goals_conceded=1)
        self.assertEqual(tracker.matches_played, 1)
        self.assertEqual(tracker.wins, 1)
        self.assertEqual(tracker.draws, 0)
        self.assertEqual(tracker.losses, 0)
        self.assertEqual(tracker.points, 3)
        self.assertEqual(tracker.goal_difference, 2)

        # Draw: 2-2
        tracker.record_match_stats(goals_scored=2, goals_conceded=2)
        self.assertEqual(tracker.matches_played, 2)
        self.assertEqual(tracker.wins, 1)
        self.assertEqual(tracker.draws, 1)
        self.assertEqual(tracker.points, 4)
        self.assertEqual(tracker.goal_difference, 2)

        # Loss: 0-1
        tracker.record_match_stats(goals_scored=0, goals_conceded=1)
        self.assertEqual(tracker.matches_played, 3)
        self.assertEqual(tracker.losses, 1)
        self.assertEqual(tracker.points, 4)
        self.assertEqual(tracker.goal_difference, 1)

        tracker.reset_stats()
        self.assertEqual(tracker.matches_played, 0)
        self.assertEqual(tracker.points, 0)

    def test_person_encapsulation_and_age_validation(self):
        person = Person("Alex Morgan", 28)
        self.assertEqual(person.name, "Alex Morgan")
        self.assertEqual(person.age, 28)

        # Valid mutator
        person.age = 29
        self.assertEqual(person.age, 29)

        # Invalid mutators
        with self.assertRaises(ValueError):
            person.age = -5
        with self.assertRaises(ValueError):
            person.age = 0
        with self.assertRaises(ValueError):
            person.age = 150
        with self.assertRaises(ValueError):
            person.age = "twenty"


class TestPlayerModel(unittest.TestCase):
    """Tests for Player single inheritance and functionality."""

    def test_valid_player_creation(self):
        player = Player("P1", "Lionel Messi", 36, "Forward", 10, 5)
        self.assertTrue(isinstance(player, Person))
        self.assertEqual(player.player_id, "P1")
        self.assertEqual(player.name, "Lionel Messi")
        self.assertEqual(player.age, 36)
        self.assertEqual(player.position, "Forward")
        self.assertEqual(player.goals_scored, 10)
        self.assertEqual(player.assists, 5)

    def test_invalid_player_age(self):
        with self.assertRaises(ValueError):
            Player("P2", "Kylian Mbappe", -1, "Forward")
        with self.assertRaises(ValueError):
            Player("P3", "Erling Haaland", 0, "Forward")

    def test_player_stats_increment(self):
        player = Player("P4", "Kevin De Bruyne", 32, "Midfielder")
        player.add_goals(2)
        player.add_assists(3)
        self.assertEqual(player.goals_scored, 2)
        self.assertEqual(player.assists, 3)

        with self.assertRaises(ValueError):
            player.add_goals(-1)

    def test_player_serialization(self):
        player = Player("P5", "Luka Modric", 38, "Midfielder", 2, 8)
        data = player.to_dict()
        restored = Player.from_dict(data)

        self.assertEqual(restored.player_id, player.player_id)
        self.assertEqual(restored.name, player.name)
        self.assertEqual(restored.age, player.age)
        self.assertEqual(restored.position, player.position)
        self.assertEqual(restored.goals_scored, player.goals_scored)
        self.assertEqual(restored.assists, player.assists)

    def test_player_str_representation(self):
        player = Player("P1", "Bukayo Saka", 22, "Forward", 5, 4)
        text = str(player)
        self.assertIn("Bukayo Saka", text)
        self.assertIn("Forward", text)
        self.assertIn("Goals: 5", text)


class TestTeamModel(unittest.TestCase):
    """Tests for Team multiple inheritance and roster management."""

    def test_team_creation_and_multiple_inheritance(self):
        team = Team("T1", "Arsenal")
        self.assertTrue(isinstance(team, Identifiable))
        self.assertTrue(isinstance(team, StatsTracker))
        self.assertEqual(team.team_id, "T1")
        self.assertEqual(team.name, "Arsenal")
        self.assertEqual(team.matches_played, 0)
        self.assertEqual(len(team), 0)

    def test_adding_and_removing_players(self):
        team = Team("T2", "Chelsea")
        p1 = Player("P10", "Cole Palmer", 21, "Midfielder")
        p2 = Player("P11", "Enzo Fernandez", 23, "Midfielder")

        team.add_player(p1)
        team.add_player(p2)
        self.assertEqual(len(team), 2)
        self.assertEqual(team.get_player_count(), 2)

        # Attempt duplicate player
        with self.assertRaises(ValueError):
            team.add_player(p1)

        # Find player
        found = team.find_player("P10")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Cole Palmer")

        # Remove player
        removed = team.remove_player("P10")
        self.assertEqual(removed.player_id, "P10")
        self.assertEqual(len(team), 1)

        # Remove nonexistent player
        with self.assertRaises(ValueError):
            team.remove_player("NONEXISTENT")

    def test_team_serialization(self):
        team = Team("T3", "Liverpool")
        p = Player("P20", "Mohamed Salah", 31, "Forward", 15, 9)
        team.add_player(p)
        team.record_match_stats(goals_scored=3, goals_conceded=0)

        data = team.to_dict()
        restored = Team.from_dict(data)

        self.assertEqual(restored.id, team.id)
        self.assertEqual(restored.name, team.name)
        self.assertEqual(restored.wins, 1)
        self.assertEqual(restored.points, 3)
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored.roster[0].name, "Mohamed Salah")


class TestMatchModel(unittest.TestCase):
    """Tests for Match creation, validation, score recording, and outcomes."""

    def setUp(self):
        self.team_a = Team("T1", "Real Madrid")
        self.team_b = Team("T2", "Barcelona")

    def test_valid_match_creation(self):
        match = Match("M1", self.team_a, self.team_b, round_number=1)
        self.assertEqual(match.match_id, "M1")
        self.assertEqual(match.home_team.name, "Real Madrid")
        self.assertEqual(match.away_team.name, "Barcelona")
        self.assertEqual(match.round_number, 1)
        self.assertFalse(match.is_played)
        self.assertIsNone(match.home_score)
        self.assertIsNone(match.away_score)
        self.assertIsNone(match.winner)

    def test_team_cannot_play_itself(self):
        with self.assertRaises(ValueError):
            Match("M2", self.team_a, self.team_a, round_number=1)

    def test_invalid_negative_score(self):
        match = Match("M3", self.team_a, self.team_b, round_number=1)
        self.assertFalse(Match.validate_score(-1))
        self.assertTrue(Match.validate_score(0))
        self.assertTrue(Match.validate_score(4))

        with self.assertRaises(ValueError):
            match.record_result(-1, 2)
        with self.assertRaises(ValueError):
            match.record_result(2, -3)

    def test_recording_match_result_and_team_stats(self):
        match = Match("M4", self.team_a, self.team_b, round_number=1)
        match.record_result(home_score=3, away_score=1)

        self.assertTrue(match.is_played)
        self.assertEqual(match.home_score, 3)
        self.assertEqual(match.away_score, 1)
        self.assertEqual(match.winner, self.team_a)
        self.assertFalse(match.is_draw)

        # Check that team statistics were updated automatically
        self.assertEqual(self.team_a.matches_played, 1)
        self.assertEqual(self.team_a.wins, 1)
        self.assertEqual(self.team_a.points, 3)
        self.assertEqual(self.team_a.goals_for, 3)
        self.assertEqual(self.team_a.goals_against, 1)

        self.assertEqual(self.team_b.matches_played, 1)
        self.assertEqual(self.team_b.losses, 1)
        self.assertEqual(self.team_b.points, 0)
        self.assertEqual(self.team_b.goals_for, 1)
        self.assertEqual(self.team_b.goals_against, 3)

        # Attempt to re-record match should fail
        with self.assertRaises(ValueError):
            match.record_result(1, 1)

    def test_draw_outcome(self):
        match = Match("M5", self.team_a, self.team_b, round_number=2)
        match.record_result(home_score=2, away_score=2)

        self.assertTrue(match.is_played)
        self.assertIsNone(match.winner)
        self.assertTrue(match.is_draw)
        self.assertEqual(self.team_a.points, 1)
        self.assertEqual(self.team_b.points, 1)


if __name__ == "__main__":
    unittest.main()
