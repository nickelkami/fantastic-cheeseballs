from espn import init_league
from itertools import groupby, product
import random
import argparse
from ext_team import ExtTeam


def break_ties(tied_teams, h2h):
    final_order = []

    remaining = tied_teams.copy()

    while remaining:
        if len(remaining) == 1:
            final_order.append(remaining[0])
            return final_order
        game_counts = []
        h2h_records = {}
        for team in remaining:
            wins = 0
            losses = 0
            for opp in remaining:
                if opp is team:
                    continue
                wins += team.wins_vs.get(opp.espn_team.team_id, 0)
                losses += team.losses_vs.get(opp.espn_team.team_id, 0)
            game_counts.append(wins + losses)
            h2h_records[team] = (wins, losses)

        # they have all played the same non-zero number of times and league uses h2h tiebreakers
        if len(set(game_counts)) == 1 and game_counts[0] > 0 and h2h:
            for team, (wins, losses) in h2h_records.items():
                team.h2h_pct = wins / (wins + losses) if (wins + losses) > 0 else 0

            max_h2h = max(team.h2h_pct for team in remaining)
            top_teams = [t for t in remaining if t.h2h_pct == max_h2h]
            if len(top_teams) == 1:
                final_order.append(top_teams[0])
                remaining.remove(top_teams[0])
            else:
                top_teams_sorted = sorted(top_teams, key=lambda t: t.points, reverse=True)
                final_order.append(top_teams_sorted[0])
                remaining.remove(top_teams_sorted[0])

        else:
            top_teams_sorted = sorted(remaining, key=lambda t: t.points, reverse=True)
            final_order.append(top_teams_sorted[0])
            remaining.remove(top_teams_sorted[0])

    return final_order


def rank_division(teams, h2h):
    """Sort teams within a division by wins, then apply tiebreakers."""
    teams_sorted = sorted(teams, key=lambda t: t.final_wins, reverse=True)
    ranked = []
    for wins, group in groupby(teams_sorted, key=lambda t: t.final_wins):
        group = list(group)
        if len(group) == 1:
            ranked.extend(group)
        else:
            ranked.extend(break_ties(group, h2h))
    return ranked


def preload_past_results(league, my_teams):
    for week in range(1, league.current_week):
        print(f"preloading week {week}...")
        for matchup in league.scoreboard(week):
            if matchup.home_score > matchup.away_score:
                my_teams[matchup.home_team.team_id].record_past_result(
                    my_teams[matchup.away_team.team_id], True
                )
                my_teams[matchup.away_team.team_id].record_past_result(
                    my_teams[matchup.home_team.team_id], False
                )
            else:
                my_teams[matchup.home_team.team_id].record_past_result(
                    my_teams[matchup.away_team.team_id], False
                )
                my_teams[matchup.away_team.team_id].record_past_result(
                    my_teams[matchup.home_team.team_id], True
                )


def get_remaining_matchups(league):
    remaining = []
    for week in range(league.current_week, league.settings.reg_season_count + 1):
        remaining.extend(league.scoreboard(week))
    return remaining


def record_matchup(my_teams, matchup, home_team_wins):
    home_team = my_teams[matchup.home_team.team_id]
    away_team = my_teams[matchup.away_team.team_id]

    home_team.record_result(away_team, home_team_wins)
    away_team.record_result(home_team, not home_team_wins)


def calculate_standings(my_teams, h2h, count_division_winners=False):
    standings = []
    divisions = {}
    for team in my_teams.values():
        divisions.setdefault(team.espn_team.division_id, []).append(team)

    winners = []
    for division_teams in divisions.values():
        ranked = rank_division(division_teams, h2h)
        winner = ranked[0]
        winners.append(winner)
        if count_division_winners:
            winner.sims_won_division += 1

    if len(winners) == 2:
        if winners[0].final_wins == winners[1].final_wins:
            standings.extend(break_ties(winners, h2h))
        else:
            standings.extend(winners)
    else:
        standings.extend(winners)

    sorted_teams = [team for team in my_teams.values() if team not in winners]
    sorted_teams = sorted(sorted_teams, key=lambda team: team.final_wins, reverse=True)

    for _, group in groupby(sorted_teams, key=lambda team: team.final_wins):
        tied_group = list(group)
        if len(tied_group) == 1:
            standings.extend(tied_group)
        else:
            standings.extend(break_ties(tied_group, h2h))

    return standings


def reset_simulation(my_teams):
    for team in my_teams.values():
        team.reset_sim()


def record_standings(standings):
    for place, team in enumerate(standings, start=1):
        team.sims_finished_at[place] = team.sims_finished_at.get(place, 0) + 1


def monte_carlo(league, my_teams, h2h, iterations=1000):
    remaining_matchups = get_remaining_matchups(league)

    print()
    for iteration in range(1, iterations + 1):
        print(f"\rSimulating iteration {iteration} / {iterations}...", end="", flush=True)
        for matchup in remaining_matchups:
            home_team_wins = random.choice((True, False))
            record_matchup(my_teams, matchup, home_team_wins)

        standings = calculate_standings(my_teams, h2h, count_division_winners=True)
        record_standings(standings)
        reset_simulation(my_teams)


def exhaustive(league, my_teams, h2h):
    remaining_matchups = get_remaining_matchups(league)
    outcome_count = 2 ** len(remaining_matchups)

    print(f"Exhaustively evaluating {outcome_count:,} possible outcomes "
          f"for {len(remaining_matchups)} remaining matchups...")

    for outcome_number, outcome in enumerate(
        product((True, False), repeat=len(remaining_matchups)), start=1
    ):
        print(f"\rEvaluating outcome {outcome_number:,} / {outcome_count:,}...", end="", flush=True)

        for matchup, home_team_wins in zip(remaining_matchups, outcome):
            record_matchup(my_teams, matchup, home_team_wins)

        standings = calculate_standings(my_teams, h2h, count_division_winners=True)
        record_standings(standings)
        reset_simulation(my_teams)


def print_results(my_teams, outcome_count):
    print("\n")
    for team in my_teams.values():
        print(f"Data for {team.espn_team.team_name}")
        print(f"Best possible placing: {min(team.sims_finished_at)}")
        print(f"Worst possible placing: {max(team.sims_finished_at)}")
        print(f"Times winning {team.espn_team.division_name} division: {team.sims_won_division}")
        print("Distribution:")
        for place, count in sorted(team.sims_finished_at.items()):
            percentage = count / outcome_count * 100
            print(f"{place} --- {count} times ({percentage:.2f}%)")
        print()


def parse_args():
    parser = argparse.ArgumentParser(description="Simulate fantasy football final standings.")
    parser.add_argument(
        "method",
        nargs="?",
        choices=("monte-carlo", "exhaustive"),
        default="monte-carlo",
        help="Simulation method (default: monte-carlo)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of Monte Carlo iterations (default: 1000)",
    )
    parser.add_argument(
        "--points-tiebreaker",
        action="store_true",
        help="Use total points instead of head-to-head tiebreakers",
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    league = init_league()
    my_teams = {team.team_id: ExtTeam(team) for team in league.teams}

    preload_past_results(league, my_teams)

    h2h = not args.points_tiebreaker
    if args.method == "exhaustive":
        remaining_matchups = get_remaining_matchups(league)
        outcome_count = 2 ** len(remaining_matchups)
        exhaustive(league, my_teams, h2h)
    else:
        outcome_count = args.iterations
        monte_carlo(league, my_teams, h2h, args.iterations)

    print_results(my_teams, outcome_count)