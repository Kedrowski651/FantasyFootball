"""Utilities for interacting with NFL.com fantasy league API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover - handled at runtime
    requests = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - handled at runtime
    BeautifulSoup = None  # type: ignore

API_URL_TEMPLATE = "https://fantasy.nfl.com/league/{league_id}/settings?format=json"

__all__ = ["fetch_league_data", "fetch_league_standings"]

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

    # The NFL.com endpoint sometimes returns an HTML document (for example when
    # the league is private or the ID is invalid).  Attempting to decode such a
    # response as JSON results in a cryptic ``JSONDecodeError`` message like
    # ``Expecting value: line 1 column 1``.  To provide a clearer error we
    # validate that the response claims to contain JSON before decoding and, if
    # decoding still fails, raise a ``ValueError`` with a helpful message.
    content_type = response.headers.get("Content-Type", "")
    if "json" not in content_type.lower():
        raise ValueError(
            "NFL.com did not return JSON data; the league may be private or the ID may be invalid."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError("NFL.com returned malformed JSON data") from exc


def fetch_league_standings(
    league_id: str, session: Optional[object] = None
) -> List[Dict[str, str]]:
    """Fetch standings table for the given league ID from NFL.com.

    Parameters
    ----------
    league_id: str
        The identifier of the fantasy league on NFL.com.
    session: object, optional
        Object with a ``get`` method returning a response with ``text`` and
        ``raise_for_status`` attributes. If ``None`` the function attempts to
        use :mod:`requests`.

    Returns
    -------
    list of dict
        Each dictionary represents a team with keys ``team``, ``wlt``, ``pct``,
        ``pts_for`` and ``pts_against``.
    """

    sess = session or requests
    if sess is None:  # pragma: no cover - executed only when requests missing
        raise RuntimeError(
            "The requests library is required to fetch league standings"
        )
    if BeautifulSoup is None:  # pragma: no cover - executed only when bs4 missing
        raise RuntimeError(
            "The bs4 library is required to parse league standings"
        )

    url = f"https://fantasy.nfl.com/league/{league_id}"
    response = sess.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    standings: List[Dict[str, str]] = []
    rows = soup.select("table.tableType-team.hasGroups tbody tr")
    for row in rows:
        def cell_text(selector: str) -> str:
            cell = row.select_one(selector)
            return cell.get_text(strip=True) if cell else ""

        standings.append(
            {
                "team": cell_text("td.team"),
                "wlt": cell_text("td.wlt"),
                "pct": cell_text("td.pct"),
                "pts_for": cell_text("td.pts_for"),
                "pts_against": cell_text("td.pts_against"),
            }
        )

    return standings
