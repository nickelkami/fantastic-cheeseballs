from espn import init_league
from itertools import groupby
import random

class ExtTeam:
    def __init__(self, espn_team):
        self.espn_team = espn_team
        self.remaining_opponents = []
        self.playoff_odds = None
        self.seed = None
        
        self.wins = espn_team.wins
        self.losses = espn_team.losses
        self.points = espn_team.points_for
        
        # sim specific variables
        self.final_wins = espn_team.wins
        self.final_losses = espn_team.losses
        self.wins_vs = {}
        self.losses_vs = {}

        self.h2h_pct = 0

        # self.initialize_sched()

    def record_result(self, opponent, did_win):
        if did_win:
            self.final_wins += 1
            self.wins_vs[opponent.espn_team.team_id] = self.wins_vs.get(opponent.espn_team.team_id, 0) + 1
        else:
            self.final_losses += 1
            self.losses_vs[opponent.espn_team.team_id] = self.losses_vs.get(opponent.espn_team.team_id, 0) + 1

    @property
    def name(self):
        return self.espn_team.team_name
    
    
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


def monte_carlo(league, my_teams, iterations=10000):
    # standings = league.standings()
    # results = {team: 0 for team in standings}
    # for _ in range(iterations):
    # print(f"simulation {i}/{iterations}...\n")

    for i in range(league.current_week, league.settings.reg_season_count + 1):
        print(f"simulating week {i}...")
        matchups = league.scoreboard(i)
        for m in matchups:
            y = random.randrange(1, 11)
            if y % 2 == 0:
                my_teams[m.home_team.team_id - 1].record_result(my_teams[m.away_team.team_id - 1], True)
                my_teams[m.away_team.team_id - 1].record_result(my_teams[m.home_team.team_id - 1], False)
                print(f"{m.home_team.team_name} defeats {m.away_team.team_name}")
            else:
                my_teams[m.home_team.team_id - 1].record_result(my_teams[m.away_team.team_id - 1], False)
                my_teams[m.away_team.team_id - 1].record_result(my_teams[m.home_team.team_id - 1], True)
                print(f"{m.home_team.team_name} defeats {m.away_team.team_name}")
        print("\n")

    sorted_teams = sorted(
        my_teams,
        key=lambda t: t.final_wins,
        reverse=True
    )

    standings = []
    groups = []
    for wins, group in groupby(sorted_teams, key=lambda t: t.final_wins):
        tied_group = list(group)
        if len(tied_group) == 1:
            standings.extend(tied_group)
        else:
            standings.extend(break_ties(tied_group))

    for i, team in enumerate(standings):
        print(f"{i + 1}//{team.espn_team.team_name}: {team.final_wins} - {team.final_losses} ({round(team.points, 2)})")
    #     for (a, b), p in zip(matchups):
    #         winner = a if random.random() < p else b
    #         s[winner] += 1
    #     top_teams = sorted(s.items(), key=lambda x: x[1], reverse=True)[:4]
    #     for team, _ in top_teams:
    #         results[team] += 1
    # for team in results:
    #     results[team] /= iterations
    return


if __name__ == '__main__':
    league = init_league()

    my_teams = [ExtTeam(team) for team in league.teams]

    monte_carlo(league, my_teams)