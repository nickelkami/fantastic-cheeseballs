class ExtTeam:
    def __init__(self, espn_team):
        # preexisting values
        self.espn_team = espn_team
        self.wins = espn_team.wins
        self.losses = espn_team.losses
        self.points = espn_team.points_for

        self.existing_wins_vs = {}
        self.existing_losses_vs = {}
        
        # sim specific variables
        self.final_wins = espn_team.wins
        self.final_losses = espn_team.losses
        self.wins_vs = self.existing_wins_vs
        self.losses_vs = self.existing_losses_vs
        self.h2h_pct = 0

        # meta variables
        self.sims_finished_at = {}

    def record_past_result(self, opponent, did_win):
        if did_win:
            self.wins_vs[opponent.espn_team.team_id] = self.wins_vs.get(opponent.espn_team.team_id, 0) + 1
        else:
            self.losses_vs[opponent.espn_team.team_id] = self.losses_vs.get(opponent.espn_team.team_id, 0) + 1

    def record_result(self, opponent, did_win):
        if did_win:
            self.final_wins += 1
            self.wins_vs[opponent.espn_team.team_id] = self.wins_vs.get(opponent.espn_team.team_id, 0) + 1
        else:
            self.final_losses += 1
            self.losses_vs[opponent.espn_team.team_id] = self.losses_vs.get(opponent.espn_team.team_id, 0) + 1

    def reset_sim(self):
        self.final_wins = self.espn_team.wins
        self.final_losses = self.espn_team.losses
        self.wins_vs = self.existing_wins_vs
        self.losses_vs = self.existing_losses_vs
        self.h2h_pct = 0

    @property
    def name(self):
        return self.espn_team.team_name