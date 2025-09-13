# Fantasy Football Dashboard

This project collects utilities and experimentation for building a dashboard around NFL.com fantasy leagues. Core features include:

- Playoff clinching probabilities (Monte Carlo simulation)
- Paths to elimination / playoff scenarios
- League dashboards with metrics your league will enjoy

**League example:** I use NFL.com each year.
League link: https://fantasy.nfl.com/league/845342 (ID: 845342)

## Playoff Probability Simulator

The `playoff_probability.py` module contains a simple simulator. Provide your league's current standings and remaining schedule, and it will estimate the chance that each team makes the playoffs.

### Example

```bash
python playoff_probability.py
```

## Dashboard

A minimal Streamlit dashboard accepts an NFL.com league ID and displays raw league data.

Run it locally with:

```bash
streamlit run dashboard.py
```

The app will prompt for your league ID and attempt to fetch data from the NFL.com API.

## Fetching league standings

The API module also includes a convenience wrapper for retrieving the current
league table.

```python
from league_api import fetch_league_standings

standings = fetch_league_standings("845342")
for team in standings:
    print(f"{team['name']}: {team['wins']}-{team['losses']}")
```

Sample output:

```
Sharks: 7-1
Jets: 5-3
Tigers: 2-6
```
