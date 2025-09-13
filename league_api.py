"""Utilities for interacting with NFL.com fantasy league API."""
from __future__ import annotations

from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover - handled at runtime
    requests = None  # type: ignore

API_URL_TEMPLATE = "https://fantasy.nfl.com/league/{league_id}/settings?format=json"

def fetch_league_data(league_id: str, session: Optional[object] = None) -> Dict[str, Any]:
    """Fetch JSON data for the given league ID from NFL.com.

    Parameters
    ----------
    league_id: str
        The identifier of the fantasy league on NFL.com.
    session: object, optional
        Object with a ``get`` method returning a response with ``json`` and
        ``raise_for_status`` attributes. If ``None`` the function attempts to
        use :mod:`requests`.

    Returns
    -------
    dict
        Parsed JSON document describing the league.
    """
    sess = session or requests
    if sess is None:  # pragma: no cover - executed only when requests missing
        raise RuntimeError("The requests library is required to fetch league data")
    url = API_URL_TEMPLATE.format(league_id=league_id)
    response = sess.get(url)
    response.raise_for_status()
    return response.json()
