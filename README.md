# Fantasy Football Dashboard

This project collects utilities and experimentation for building a dashboard around NFL.com fantasy leagues. Core features include:

- Playoff clinching probabilities (Monte Carlo simulation)
- Paths to elimination / playoff scenarios
- League dashboards with metrics your league will enjoy

**League example:** I use NFL.com each year.
League link: https://fantasy.nfl.com/league/845342 (ID: 845342)

## Installation

Install core dependencies with pip:

```bash
pip install -r requirements.txt
```

`beautifulsoup4` is optional and only required for HTML scraping features.

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
