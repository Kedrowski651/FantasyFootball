import sys
from pathlib import Path

# Add project root to module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from playoff_probability import Team, Matchup, simulate_season


def test_simulation_returns_probabilities():
    teams = {
        "A": Team("A"),
        "B": Team("B"),
        "C": Team("C"),
        "D": Team("D"),
    }
    matchups = [Matchup(1, "A", "B"), Matchup(1, "C", "D")]
    probs = simulate_season(teams, matchups, sims=10, playoff_teams=4)
    assert len(probs) == 4
    # With four teams and four playoff slots, every team qualifies
    for p in probs.values():
        assert abs(p - 1.0) < 1e-6
