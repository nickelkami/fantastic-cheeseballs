from espn import init_league

class ExtTeam:
    def __init__(self, espn_team):
        self.espn_team = espn_team
        self.remaining_opponents = []
        self.playoff_odds = None
        self.seed = None
        

        self.initialize_stats()

    def initialize_stats(self):
        for i in range(1, 18):
            box_scores = league.scoreboard(i)
            if not box_scores:
                break
            if box_scores[0].home_score == 0:
                for matchup in box_scores:
                    if matchup.home_team == self.espn_team:
                        self.remaining_opponents.append(matchup.away_team)
                        break
                    if matchup.away_team == self.espn_team:
                        self.remaining_opponents.append(matchup.home_team)
                        break

    @property
    def name(self):
        return self.espn_team.team_name

def monte_carlo(league, iterations=10000):
    # standings = league.standings()

    # results = {team: 0 for team in standings}
    # for _ in range(iterations):
    #     s = standings.copy()
    #     for (a, b), p in zip(matchups, win_probs):
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

    for t in my_teams:
        print(f"{t.espn_team.team_name} remaining schedule:\n")
        for x in t.remaining_opponents:
            print(f"{x.team_name}")
        print("\n")
    # monte_carlo()