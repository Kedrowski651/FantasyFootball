"""Simple Monte Carlo playoff probability simulator for NFL.com fantasy leagues.

This module contains lightweight data structures and a simulation function that
can be used to estimate playoff clinching probabilities. It does not interact
with the NFL.com API directly; instead, it expects basic league information
about each team and remaining scheduled matchups.

Example
-------
>>> from playoff_probability import Team, Matchup, simulate_season
>>> teams = {
...     'A': Team('A', 3, 0),
...     'B': Team('B', 2, 1),
...     'C': Team('C', 1, 2),
...     'D': Team('D', 0, 3)
... }
>>> schedule = [Matchup(week=4, team1='A', team2='B'),
...             Matchup(week=4, team1='C', team2='D')]
>>> simulate_season(teams, schedule, sims=1000)  # doctest: +SKIP
{'A': 0.9, 'B': 0.8, 'C': 0.2, 'D': 0.1}

The simulation randomly assigns winners for every remaining matchup, tallies
final records, and then determines which teams would make the playoffs based on
regular-season record.

The module intentionally keeps things simple and can be expanded to incorporate
more advanced tie-breaking rules or integrations with live NFL.com data.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping
import random


@dataclass(frozen=True)
class Team:
    """Represents a fantasy team with current win/loss record."""

    name: str
    wins: int = 0
    losses: int = 0


@dataclass(frozen=True)
class Matchup:
    """Represents a future matchup between two teams."""

    week: int
    team1: str
    team2: str


def simulate_season(
    teams: Mapping[str, Team],
    matchups: Iterable[Matchup],
    sims: int = 1000,
    playoff_teams: int = 4,
) -> Dict[str, float]:
    """Run a Monte Carlo simulation of the remaining season.

    Parameters
    ----------
    teams:
        Mapping of team name to :class:`Team` object containing their current
        record.
    matchups:
        Iterable of future :class:`Matchup` objects that have yet to be played.
    sims:
        Number of simulation runs to perform.
    playoff_teams:
        Number of teams that qualify for the playoffs.

    Returns
    -------
    dict
        A mapping of team name to the probability of making the playoffs.
    """

    clinched = defaultdict(int)
    matchups = list(matchups)

    for _ in range(sims):
        # Copy records for this simulation run
        records: Dict[str, List[int]] = {
            name: [team.wins, team.losses] for name, team in teams.items()
        }

        # Randomly determine winners for remaining matchups
        for m in matchups:
            winner = random.choice([m.team1, m.team2])
            loser = m.team2 if winner == m.team1 else m.team1
            records[winner][0] += 1
            records[loser][1] += 1

        # Sort by wins descending, then losses ascending
        standings = sorted(
            records.items(), key=lambda item: (-item[1][0], item[1][1])
        )
        qualifiers = [name for name, _ in standings[:playoff_teams]]
        for name in qualifiers:
            clinched[name] += 1

    return {name: clinched[name] / sims for name in teams.keys()}


if __name__ == "__main__":
    # A tiny example when running the module directly
    example_teams = {
        "Alpha": Team("Alpha", 5, 2),
        "Bravo": Team("Bravo", 4, 3),
        "Charlie": Team("Charlie", 3, 4),
        "Delta": Team("Delta", 2, 5),
    }
    example_schedule = [
        Matchup(week=8, team1="Alpha", team2="Bravo"),
        Matchup(week=8, team1="Charlie", team2="Delta"),
    ]

    probs = simulate_season(example_teams, example_schedule, sims=1000)
    for team, prob in probs.items():
        print(f"{team}: {prob:.1%} chance to make playoffs")
