"""
Menu interface for TournaCore terminal application.
Demonstrates:
- Classes and objects
- Instance methods and self
- Encapsulation of application state
- Integration of Tournament, Team, Player, Match, and StatsService
- Beginner-friendly input/output handling with clear validation
"""
from models.tournament import LeagueTournament
from models.team import Team
from models.player import Player


class CLIApp:
    """
    Terminal interface for the TournaCore tournament management system.
    Manages user interaction and delegates operations to core domain models.
    """

    def __init__(self, tournament: LeagueTournament | None = None):
        self.tournament = tournament
        self.running = True

    def display_menu(self):
        """Displays the main menu options."""
        print("=" * 40)
        print("              TOURnaCORE")
        print("     Tournament Management System")
        print("=" * 40)
        if self.tournament:
            print(f"Active: {self.tournament.name} [{self.tournament.status}]")
            print("-" * 40)
        print("1. Create Tournament")
        print("2. Add Team")
        print("3. Add Player to Team")
        print("4. Generate Fixtures")
        print("5. View Fixtures")
        print("6. Record Match Result")
        print("7. View Standings")
        print("8. View Tournament Statistics")
        print("9. Exit")
        print("=" * 40)

    def run(self):
        """Main application loop."""
        while self.running:
            self.display_menu()
            choice = input("Enter choice (1-9): ").strip()
            self.handle_choice(choice)

    def handle_choice(self, choice: str):
        """Dispatches user choice to the corresponding handler method."""
        if choice == "1":
            self.create_tournament()
        elif choice == "2":
            self.add_team()
        elif choice == "3":
            self.add_player()
        elif choice == "4":
            self.generate_fixtures()
        elif choice == "5":
            self.view_fixtures()
        elif choice == "6":
            self.record_match_result()
        elif choice == "7":
            self.view_standings()
        elif choice == "8":
            self.view_statistics()
        elif choice == "9":
            self.exit_app()
        else:
            print("\n[Error] Invalid option. Please enter a number between 1 and 9.\n")

    def create_tournament(self):
        """Allows user to create a new LeagueTournament."""
        print("\n--- Create Tournament ---")
        if self.tournament:
            confirm = input(
                f"Tournament '{self.tournament.name}' is already active. "
                "Creating a new one will reset current progress. Continue? (y/n): "
            ).strip().lower()
            if confirm != "y":
                print("Tournament creation cancelled.\n")
                return

        name = input("Enter tournament name: ").strip()
        if not name:
            print("[Error] Tournament name cannot be empty.\n")
            return

        tourn_id = f"T-{name.replace(' ', '_').upper()[:6]}"
        self.tournament = LeagueTournament(tournament_id=tourn_id, name=name)
        print(f"\nTournament '{self.tournament.name}' created successfully!\n")

    def add_team(self):
        """Registers a new team into the active tournament."""
        print("\n--- Add Team ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        if self.tournament.status != "Draft":
            print("[Error] Cannot add teams after fixtures have been generated.\n")
            return

        team_name = input("Enter team name: ").strip()
        if not team_name:
            print("[Error] Team name cannot be empty.\n")
            return

        # Check for duplicate team names (case-insensitive)
        for existing in self.tournament.teams:
            if existing.name.lower() == team_name.lower():
                print(f"[Error] Team '{team_name}' is already registered.\n")
                return

        team_id = f"T{len(self.tournament.teams) + 1}"
        new_team = Team(team_id=team_id, name=team_name)

        try:
            self.tournament.register_team(new_team)
            print(f"\nTeam '{new_team.name}' (ID: {new_team.id}) added successfully!\n")
        except ValueError as e:
            print(f"[Error] {e}\n")

    def add_player(self):
        """Adds a player to a selected team."""
        print("\n--- Add Player to Team ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        teams = self.tournament.teams
        if not teams:
            print("[Error] No teams registered yet. Please add a team first (Option 2).\n")
            return

        print("Select a team:")
        for idx, team in enumerate(teams, start=1):
            print(f"  {idx}. {team.name} (Players: {len(team)})")

        choice = input(f"Enter team number (1-{len(teams)}): ").strip()
        if not choice.isdigit():
            print("[Error] Invalid selection. Please enter a valid number.\n")
            return

        team_idx = int(choice) - 1
        if team_idx < 0 or team_idx >= len(teams):
            print("[Error] Team number out of range.\n")
            return

        selected_team = teams[team_idx]

        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        if not first_name or not last_name:
            print("[Error] First name and last name cannot be empty.\n")
            return

        full_name = f"{first_name} {last_name}"

        age_input = input("Enter age: ").strip()
        if not age_input.isdigit():
            print("[Error] Age must be a positive integer.\n")
            return
        age = int(age_input)
        if age <= 0 or age > 120:
            print("[Error] Age must be between 1 and 120.\n")
            return

        jersey_input = input("Enter jersey number: ").strip()
        if not jersey_input.isdigit() or int(jersey_input) <= 0:
            print("[Error] Jersey number must be a positive integer.\n")
            return
        jersey_num = int(jersey_input)

        # Unique player ID based on jersey in team
        player_id = f"P{jersey_num}"
        if selected_team.find_player(player_id) is not None:
            print(f"[Error] Jersey #{jersey_num} is already taken on team '{selected_team.name}'.\n")
            return

        valid_positions = Player.VALID_POSITIONS
        pos_list = "/".join(valid_positions)
        position_input = input(f"Enter position ({pos_list}) [default: Player]: ").strip().capitalize()
        if not position_input:
            position_input = "Player"

        if position_input not in valid_positions:
            print(f"[Error] Invalid position '{position_input}'. Allowed: {pos_list}\n")
            return

        try:
            player = Player(
                player_id=player_id,
                name=full_name,
                age=age,
                position=position_input,
            )
            selected_team.add_player(player)
            print(
                f"\nPlayer '{player.name}' (#{jersey_num}, {player.position}) "
                f"added to '{selected_team.name}' successfully!\n"
            )
        except (ValueError, TypeError) as e:
            print(f"[Error] Failed to add player: {e}\n")

    def generate_fixtures(self):
        """Generates round-robin fixtures using the tournament model."""
        print("\n--- Generate Fixtures ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        if len(self.tournament.teams) < 2:
            print(
                f"[Error] At least 2 teams are required to generate fixtures. "
                f"Currently registered: {len(self.tournament.teams)}.\n"
            )
            return

        if self.tournament.matches:
            print("[Error] Fixtures have already been generated for this tournament.\n")
            return

        try:
            fixtures = self.tournament.generate_fixtures()
            print(f"\nFixtures generated successfully! Total matches scheduled: {len(fixtures)}.\n")
        except ValueError as e:
            print(f"[Error] {e}\n")

    def view_fixtures(self):
        """Displays all scheduled and completed matches grouped by round."""
        print("\n--- Tournament Fixtures ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        matches = self.tournament.matches
        if not matches:
            print("[Info] No fixtures generated yet. Please generate fixtures first (Option 4).\n")
            return

        # Group matches by round number
        rounds: dict[int, list] = {}
        for m in matches:
            rounds.setdefault(m.round_number, []).append(m)

        for round_num in sorted(rounds.keys()):
            print(f"\nRound {round_num}")
            print("-" * 40)
            for m in rounds[round_num]:
                if m.is_played:
                    print(f"[{m.match_id}] {m.home_team.name} {m.home_score} - {m.away_score} {m.away_team.name} (FT)")
                else:
                    print(f"[{m.match_id}] {m.home_team.name} vs {m.away_team.name} (Not played)")
        print()

    def record_match_result(self):
        """Allows user to enter scores for an unplayed match."""
        print("\n--- Record Match Result ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        matches = self.tournament.matches
        if not matches:
            print("[Error] No fixtures available. Please generate fixtures first (Option 4).\n")
            return

        unplayed = self.tournament.get_upcoming_matches()
        if not unplayed:
            print("[Info] All scheduled matches have already been completed!\n")
            return

        print("Unplayed Matches:")
        for idx, m in enumerate(unplayed, start=1):
            print(f"  {idx}. [{m.match_id}] [Round {m.round_number}] {m.home_team.name} vs {m.away_team.name}")

        selection = input(f"Select match (1-{len(unplayed)} or Match ID, 'c' to cancel): ").strip()
        if selection.lower() == "c":
            print("Operation cancelled.\n")
            return

        chosen_match = None
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(unplayed):
                chosen_match = unplayed[idx]
        else:
            # Check by match_id
            for m in unplayed:
                if m.match_id.lower() == selection.lower():
                    chosen_match = m
                    break

        if not chosen_match:
            print("[Error] Invalid match selection.\n")
            return

        print(f"\nSelected: {chosen_match.home_team.name} vs {chosen_match.away_team.name}")

        home_input = input(f"Enter {chosen_match.home_team.name} score: ").strip()
        if not home_input.isdigit():
            print("[Error] Score must be a non-negative integer.\n")
            return
        home_score = int(home_input)

        away_input = input(f"Enter {chosen_match.away_team.name} score: ").strip()
        if not away_input.isdigit():
            print("[Error] Score must be a non-negative integer.\n")
            return
        away_score = int(away_input)

        try:
            self.tournament.record_match_result(
                match_id=chosen_match.match_id,
                home_score=home_score,
                away_score=away_score,
            )
            print(
                f"\nResult recorded successfully: "
                f"{chosen_match.home_team.name} {home_score} - {away_score} {chosen_match.away_team.name}\n"
            )
            if self.tournament.status == "Completed":
                print("*** Tournament Complete! All matches have been played. ***\n")
        except ValueError as e:
            print(f"[Error] Failed to record result: {e}\n")

    def view_standings(self):
        """Displays the league standings table."""
        print("\n--- League Standings ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        if not self.tournament.teams:
            print("[Info] No teams registered in the tournament.\n")
            return

        standings = self.tournament.get_standings()

        title = f"STANDINGS: {self.tournament.name}"
        width = 66
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
        print(f"{'Pos':<4} {'Team':<20} {'P':>3} {'W':>3} {'D':>3} {'L':>3} {'GF':>4} {'GA':>4} {'GD':>4} {'Pts':>4}")
        print("-" * width)

        for pos, row in enumerate(standings, start=1):
            gd_str = f"{row.goal_difference:+d}"
            print(
                f"{pos:<4} {row.team.name:<20} {row.played:>3} {row.wins:>3} "
                f"{row.draws:>3} {row.losses:>3} {row.goals_for:>4} "
                f"{row.goals_against:>4} {gd_str:>4} {row.points:>4}"
            )
        print("=" * width)
        print()

    def view_statistics(self):
        """Displays tournament summary statistics."""
        print("\n--- Tournament Statistics ---")
        if not self.tournament:
            print("[Error] No active tournament. Please create a tournament first (Option 1).\n")
            return

        stats = self.tournament.get_statistics()

        title = f"STATISTICS: {self.tournament.name}"
        width = 56
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)

        print(f"  Total Teams Registered:         {stats['total_teams']}")
        print(f"  Total Matches Scheduled:        {stats['total_matches']}")
        print(f"  Matches Completed:              {stats['completed_matches']}")
        print(f"  Total Goals Scored:             {stats['total_goals']}")
        print(f"  Average Goals per Match:        {stats['average_goals_per_match']}")

        highest_team = stats["highest_scoring_team"]
        highest_text = (
            f"{highest_team.name} ({highest_team.goals_for} goals)"
            if highest_team is not None
            else "No data available"
        )
        print(f"  Highest Scoring Team:           {highest_text}")

        best_def = stats["best_defensive_team"]
        best_def_text = (
            f"{best_def.name} ({best_def.goals_against} conceded)"
            if best_def is not None
            else "No data available"
        )
        print(f"  Best Defensive Team:            {best_def_text}")

        top_player = stats["top_scoring_player"]
        top_player_text = (
            f"{top_player.name} ({top_player.goals_scored} goals)"
            if top_player is not None
            else "No data available"
        )
        print(f"  Top Scoring Player:             {top_player_text}")

        print("=" * width)
        print()

    def exit_app(self):
        """Terminates the main application loop."""
        print("\nThank you for using TournaCore. Goodbye!\n")
        self.running = False
