"""
Unit tests for CLIApp and terminal menu interactions:
- CLI instance creation (with and without initial tournament)
- Verification that all required menu methods exist
- Creation of tournament, teams, and players via CLI logic
- Duplicate team and duplicate jersey prevention
- Tournament lifecycle operations (fixture generation, match recording)
- Safe handling of operations prior to tournament creation
- Exit operation and choice dispatching
"""
import unittest
import sys
import os
from unittest.mock import patch

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.menu import CLIApp
from models.tournament import LeagueTournament
from models.team import Team


class TestCLIApp(unittest.TestCase):
    """Tests for the terminal-based user interface logic."""

    def setUp(self):
        self.app = CLIApp()

    def test_cli_creation(self):
        """CLI can be created with default None tournament or existing tournament."""
        self.assertIsNone(self.app.tournament)
        self.assertTrue(self.app.running)

        league = LeagueTournament("L1", "Existing League")
        app_with_league = CLIApp(tournament=league)
        self.assertEqual(app_with_league.tournament, league)
        self.assertTrue(app_with_league.running)

    def test_menu_methods_exist(self):
        """All expected action handler methods must exist on CLIApp."""
        expected_methods = [
            "display_menu",
            "handle_choice",
            "create_tournament",
            "add_team",
            "add_player",
            "generate_fixtures",
            "view_fixtures",
            "record_match_result",
            "view_standings",
            "view_statistics",
            "exit_app",
            "run",
        ]
        for method_name in expected_methods:
            self.assertTrue(
                hasattr(self.app, method_name),
                f"CLIApp missing required method: {method_name}",
            )
            self.assertTrue(callable(getattr(self.app, method_name)))

    def test_exit_app(self):
        """Exit option sets running flag to False."""
        self.assertTrue(self.app.running)
        self.app.exit_app()
        self.assertFalse(self.app.running)

    def test_handle_choice_exit_and_invalid(self):
        """handle_choice dispatches '9' to exit, and handles invalid gracefully."""
        self.app.handle_choice("9")
        self.assertFalse(self.app.running)

        # Re-enable and test invalid input
        self.app.running = True
        self.app.handle_choice("invalid_number")
        self.assertTrue(self.app.running)

    @patch("builtins.input", return_value="Premier League")
    def test_create_tournament_logic(self, mock_input):
        """Creates a new tournament via CLI input."""
        self.app.create_tournament()
        self.assertIsNotNone(self.app.tournament)
        self.assertEqual(self.app.tournament.name, "Premier League")
        self.assertEqual(self.app.tournament.status, "Draft")

    @patch("builtins.input", side_effect=["Arsenal", "Arsenal", "Chelsea"])
    def test_add_team_and_prevent_duplicate(self, mock_input):
        """Adds teams and prevents registering duplicate team names."""
        self.app.tournament = LeagueTournament("L1", "EPL")

        # 1. Add 'Arsenal'
        self.app.add_team()
        self.assertEqual(len(self.app.tournament.teams), 1)
        self.assertEqual(self.app.tournament.teams[0].name, "Arsenal")

        # 2. Try duplicate 'Arsenal' (should be rejected)
        self.app.add_team()
        self.assertEqual(len(self.app.tournament.teams), 1)

        # 3. Add 'Chelsea'
        self.app.add_team()
        self.assertEqual(len(self.app.tournament.teams), 2)

    @patch("builtins.input", side_effect=["1", "Bukayo", "Saka", "22", "7", "Forward"])
    def test_add_player_to_team(self, mock_input):
        """Adds a player to a selected team."""
        self.app.tournament = LeagueTournament("L1", "EPL")
        team = Team("T1", "Arsenal")
        self.app.tournament.register_team(team)

        self.app.add_player()
        self.assertEqual(len(team.roster), 1)
        player = team.roster[0]
        self.assertEqual(player.name, "Bukayo Saka")
        self.assertEqual(player.age, 22)
        self.assertEqual(player.player_id, "P7")
        self.assertEqual(player.position, "Forward")

    @patch("builtins.input", side_effect=["1", "Declan", "Rice", "25", "7", "Midfielder"])
    def test_add_player_duplicate_jersey_prevented(self, mock_input):
        """Prevents adding two players with the same jersey number to the same team."""
        self.app.tournament = LeagueTournament("L1", "EPL")
        team = Team("T1", "Arsenal")
        self.app.tournament.register_team(team)

        # Add first player with jersey 7
        with patch("builtins.input", side_effect=["1", "Bukayo", "Saka", "22", "7", "Forward"]):
            self.app.add_player()
        self.assertEqual(len(team.roster), 1)

        # Try to add second player with same jersey 7
        self.app.add_player()
        self.assertEqual(len(team.roster), 1)

    def test_fixture_generation_and_viewing(self):
        """Generates fixtures and verifies fixtures can be viewed without error."""
        self.app.tournament = LeagueTournament("L1", "La Liga")
        self.app.tournament.register_team(Team("T1", "Real Madrid"))
        self.app.tournament.register_team(Team("T2", "Barcelona"))

        self.app.generate_fixtures()
        self.assertEqual(len(self.app.tournament.matches), 1)
        self.assertEqual(self.app.tournament.status, "In Progress")

        # Second call to generate_fixtures is blocked
        self.app.generate_fixtures()
        self.assertEqual(len(self.app.tournament.matches), 1)

        # Viewing fixtures executes cleanly
        self.app.view_fixtures()

    @patch("builtins.input", side_effect=["1", "3", "1"])
    def test_record_match_result_cli(self, mock_input):
        """Records match result through CLI prompt flow."""
        self.app.tournament = LeagueTournament("L1", "Serie A")
        t1 = Team("T1", "Milan")
        t2 = Team("T2", "Inter")
        self.app.tournament.register_team(t1)
        self.app.tournament.register_team(t2)
        self.app.tournament.generate_fixtures()

        self.app.record_match_result()
        match = self.app.tournament.matches[0]
        self.assertTrue(match.is_played)
        self.assertEqual(match.home_score, 3)
        self.assertEqual(match.away_score, 1)
        self.assertEqual(t1.points, 3)
        self.assertEqual(t2.points, 0)
        self.assertEqual(self.app.tournament.status, "Completed")

    def test_view_standings_and_statistics_without_crashing(self):
        """Standings and statistics display cleanly for populated and empty tournaments."""
        # Before tournament created
        self.app.view_standings()
        self.app.view_statistics()

        # Populated tournament
        self.app.tournament = LeagueTournament("L1", "Bundesliga")
        t1 = Team("T1", "Bayern")
        t2 = Team("T2", "Dortmund")
        self.app.tournament.register_team(t1)
        self.app.tournament.register_team(t2)
        self.app.tournament.generate_fixtures()
        self.app.tournament.record_match_result("M1", 2, 2)

        self.app.view_standings()
        self.app.view_statistics()

    def test_operations_before_tournament_created_handled_safely(self):
        """Verifies all actions handle uninitialized tournament without exceptions."""
        self.assertIsNone(self.app.tournament)
        self.app.add_team()
        self.app.add_player()
        self.app.generate_fixtures()
        self.app.view_fixtures()
        self.app.record_match_result()
        self.app.view_standings()
        self.app.view_statistics()
        self.app.display_menu()


if __name__ == "__main__":
    unittest.main()
