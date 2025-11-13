from espn import init_league
from itertools import groupby
import random
from ext_team import ExtTeam
    
def break_ties(tied_teams):
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
        
        # they have all played the same non-zero number of times
        if len(set(game_counts)) == 1 and game_counts[0] > 0:    
            for team, (wins, losses) in h2h_records.items():
                team.h2h_pct = wins / (wins + losses) if (wins + losses) > 0 else 0

            max_h2h = max(team.h2h_pct for team in remaining)
            top_teams = [t for t in remaining if t.h2h_pct == max_h2h]
            if len(top_teams) == 1:
                # Clear winner, remove and continue
                final_order.append(top_teams[0])
                remaining.remove(top_teams[0])
            else:
                # Some teams are still tied, resolve on total points
                top_teams_sorted = sorted(remaining, key=lambda t: t.points, reverse=True)
                final_order.append(top_teams_sorted[0])
                remaining.remove(top_teams_sorted[0])

        else:
            top_teams_sorted = sorted(remaining, key=lambda t: t.points, reverse=True)
            final_order.append(top_teams_sorted[0])
            remaining.remove(top_teams_sorted[0])

    return final_order


def rank_division(teams):
    """Rank teams within a division."""
    # Sort by wins, then apply tiebreakers
    teams_sorted = sorted(teams, key=lambda t: t.final_wins, reverse=True)
    ranked = []
    for wins, group in groupby(teams_sorted, key=lambda t: t.final_wins):
        group = list(group)
        if len(group) == 1:
            ranked.extend(group)
        else:
            ranked.extend(break_ties(group))
    return ranked


def monte_carlo(league, my_teams, iterations=10):
    for i in range(1, league.current_week):
        print(f"preloading week {i}...")
        matchups = league.scoreboard(i)
        for m in matchups:
            if m.home_score > m.away_score:
                my_teams[m.home_team.team_id - 1].record_past_result(my_teams[m.away_team.team_id - 1], True)
                my_teams[m.away_team.team_id - 1].record_past_result(my_teams[m.home_team.team_id - 1], False)
            else:
                my_teams[m.home_team.team_id - 1].record_past_result(my_teams[m.away_team.team_id - 1], False)
                my_teams[m.away_team.team_id - 1].record_past_result(my_teams[m.home_team.team_id - 1], True)

    print("\n")
    for iteration in range(1, iterations + 1):
        print(f"\rSimulating iteration {iteration} / {iterations}...", end="", flush=True)
        for i in range(league.current_week, league.settings.reg_season_count + 1):
            # print(f"simulating week {i}...")
            matchups = league.scoreboard(i)
            for m in matchups:
                y = random.randrange(1, 11)
                if y % 2 == 0:
                    my_teams[m.home_team.team_id - 1].record_result(my_teams[m.away_team.team_id - 1], True)
                    my_teams[m.away_team.team_id - 1].record_result(my_teams[m.home_team.team_id - 1], False)
                    # print(f"{m.home_team.team_name} defeats {m.away_team.team_name}")
                else:
                    my_teams[m.home_team.team_id - 1].record_result(my_teams[m.away_team.team_id - 1], False)
                    my_teams[m.away_team.team_id - 1].record_result(my_teams[m.home_team.team_id - 1], True)
                    # print(f"{m.away_team.team_name} defeats {m.home_team.team_name}")
            # print("\n")

        standings = []
        
        divisions = {}
        for team in my_teams:
            divisions.setdefault(team.espn_team.division_id, []).append(team)

        winners = []
        for _, division_teams in divisions.items():
            ranked = rank_division(division_teams)
            winners.append(ranked[0])
            ranked[0].sims_won_division += 1
            # print(f"{ranked[0].espn_team.division_name} division winner: {ranked[0].espn_team.team_name}")
        if len(winners) == 2:
            if winners[0].final_wins == winners[1].final_wins:
                standings.extend(break_ties(winners))
            else:
                standings.extend(winners)
        else:
            standings.extend(winners)

        sorted_teams = [t for t in my_teams if t not in winners]
        sorted_teams = sorted(
            sorted_teams,
            key=lambda t: t.final_wins,
            reverse=True
        )

        for _, group in groupby(sorted_teams, key=lambda t: t.final_wins):
            tied_group = list(group)
            if len(tied_group) == 1:
                standings.extend(tied_group)
            else:
                standings.extend(break_ties(tied_group))

        for i, team in enumerate(standings):
            team.sims_finished_at[i + 1] = team.sims_finished_at.get(i + 1, 0) + 1
            # print(f"{i + 1}//{team.espn_team.team_name} ---- {team.final_wins} - {team.final_losses} ({round(team.points, 2)})")
            team.reset_sim()


    print("\n")

    for team in my_teams:
        print(f"Data for {team.espn_team.team_name}")
        print(f"Best possible placing: {min(team.sims_finished_at)}")
        print(f"Worst possible placing {max(team.sims_finished_at)}")
        print(f"Times winning {team.espn_team.division_name} division: {team.sims_won_division}")
        print("Distribution:")
        team.sims_finished_at = dict(sorted(team.sims_finished_at.items()))
        for key, value in team.sims_finished_at.items():
            print(f"{key} --- {value} times")
        print("\n")
    return


if __name__ == '__main__':
    league = init_league()

    my_teams = [ExtTeam(team) for team in league.teams]

    monte_carlo(league, my_teams)