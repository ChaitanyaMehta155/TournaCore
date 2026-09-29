"""
Scheduler service for TournaCore.
Generates round-robin fixtures using the circle/polygon rotation algorithm.
Demonstrates:
- Static methods
- Algorithmic scheduling (Round-Robin)
- Edge case handling (Odd number of teams with BYE)
"""
from models.team import Team
from models.match import Match


class Scheduler:
    """
    Service responsible for creating balanced tournament schedules.
    """

    @staticmethod
    def generate_round_robin_fixtures(teams: list[Team]) -> list[Match]:
        """
        Generates single round-robin fixtures where each team plays every other
        team exactly once.

        Uses the standard Circle Rotation algorithm:
        - If odd number of teams, a dummy BYE is added internally.
        - Exactly N * (N - 1) / 2 matches are created.
        """
        if not teams or len(teams) < 2:
            raise ValueError("At least 2 teams are required to generate fixtures.")

        teams_list = list(teams)
        num_teams = len(teams_list)

        # If odd count, insert dummy team (None) representing a BYE
        has_bye = (num_teams % 2 != 0)
        if has_bye:
            teams_list.append(None)
            num_teams += 1

        total_rounds = num_teams - 1
        matches_per_round = num_teams // 2
        fixtures: list[Match] = []
        match_id_counter = 1

        for round_idx in range(1, total_rounds + 1):
            for i in range(matches_per_round):
                team1 = teams_list[i]
                team2 = teams_list[num_teams - 1 - i]

                # If either team is the BYE dummy, skip creating a Match
                if team1 is None or team2 is None:
                    continue

                # Alternate home and away to balance venue advantage
                if round_idx % 2 == 1:
                    home, away = team1, team2
                else:
                    home, away = team2, team1

                match = Match(
                    match_id=f"M{match_id_counter}",
                    home_team=home,
                    away_team=away,
                    round_number=round_idx,
                )
                fixtures.append(match)
                match_id_counter += 1

            # Rotate teams in circle, keeping the first team fixed at index 0
            teams_list = [teams_list[0]] + [teams_list[-1]] + teams_list[1:-1]

        return fixtures


def generate_round_robin_fixtures(teams: list[Team]) -> list[Match]:
    """Convenience functional wrapper around Scheduler.generate_round_robin_fixtures."""
    return Scheduler.generate_round_robin_fixtures(teams)
