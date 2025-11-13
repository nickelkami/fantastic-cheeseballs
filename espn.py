import requests
from espn_api.football import League
import json


def init_league():
    path = 'credentials.json' # Replace with the actual path to your JSON file
    with open(path, 'r') as file:
        creds = json.load(file)

    league = League(league_id=creds["league_id"], 
                    year=creds["year"],
                    espn_s2=creds["espn_s2"],
                    swid=creds["swid"]
            )
    
    for i, team in enumerate(league.standings()):
        print(f"{team.team_name}: {team.wins}-{team.losses} // Currently Ranked {i + 1}\n")

    return league
