# ESPN API
- This app uses 'espn-api' package found here: https://github.com/cwendt94/espn-api. This package provides a clean object definition with tons of stats and info for each ESPN Fantasy Football league

# Setup
- To set up, download the espn-api package by using 'pip install espn-api.'
- Next, find 'credentials.json' and replace 'league_id' with your league id which can be found in the URL anywhere in your league page.
- Replace 'year' with the year.
- Next, follow these steps to find your 'swid' and 'espn_s2' values - https://github.com/cwendt94/espn-api/discussions/150#discussioncomment-133615

# Usage
- Simply run 'python simulate.py' to simulate the remaining games of the season and produce a distribution of final standings.
- Note that the function by default calculates head to head as primary tiebreaker. If your league uses total points, change the third argument in the monte_carlo() function call to False to skip over h2h calculations.
- The default iterations is 1000, which currently takes about 15 minutes. To change this simply update the iterations argument in the monte_carlo() function.
