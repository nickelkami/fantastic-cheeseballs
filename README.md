# ESPN API
- This app uses 'espn-api' package found here: https://github.com/cwendt94/espn-api. This package provides a clean object definition with tons of stats and info for each ESPN Fantasy Football league

# Setup
- To set up, download the espn-api package by using 'pip install espn-api.'
- Next, find 'credentials.json' and replace 'league_id' with your league id which can be found in the URL anywhere in your league page.
- Replace 'year' with the year.
- Next, follow these steps to find your 'swid' and 'espn_s2' values - https://github.com/cwendt94/espn-api/discussions/150#discussioncomment-133615

# Usage
- Run `python simulate.py` to use the default Monte Carlo simulation with 1000 iterations.
- Run `python simulate.py monte-carlo --iterations 5000` to choose the number of Monte Carlo iterations.
- Run `python simulate.py exhaustive` to evaluate every possible result for every remaining matchup.
- Exhaustive simulation grows as `2^n`, where `n` is the number of remaining games. It is practical for a small number of remaining matchups, such as two weeks with 12 games.
- Head-to-head records are used for tiebreakers by default. Use `--points-tiebreaker` to use total points instead.
