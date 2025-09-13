# Fantasy Football Dashboard

This project collects utilities and experimentation for building a dashboard
around NFL.com fantasy leagues. One of the core features is estimating playoff
clinching probabilities using a Monte Carlo simulation.

## Playoff Probability Simulator

The `playoff_probability.py` module contains a simple simulator. Provide your
league's current standings and remaining schedule, and it will estimate the
chance that each team makes the playoffs.

### Example

```bash
python playoff_probability.py
```

The default example in the file runs a tiny simulation and prints the odds for
four sample teams. Adapt the `example_teams` and `example_schedule` variables to
use your league's real data.

### Running Tests

```bash
pytest
```

The tests include a small smoke test for the simulation logic.
