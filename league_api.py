"""Utilities for interacting with NFL.com fantasy league API."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover - handled at runtime
    requests = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - handled at runtime
    BeautifulSoup = None  # type: ignore

API_URL_TEMPLATE = "https://fantasy.nfl.com/league/{league_id}/settings?format=json"

__all__ = ["fetch_league_data", "fetch_league_standings", "parse_standings"]


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

    # Be explicit about JSON to avoid cryptic decode errors when HTML is returned.
    content_type = response.headers.get("Content-Type", "")
    if "json" not in content_type.lower():
        raise ValueError(
            "NFL.com did not return JSON data; the league may be private or the ID may be invalid."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError("NFL.com returned malformed JSON data") from exc


# -------- Regex fallback for standings parsing (works without bs4) --------

STANDING_ROW_RE = re.compile(
    r"""
    <td[^>]*class="(?:teamName|team)"[^>]*>\s*(?P<team>[^<]+)\s*</td>\s*
    <td[^>]*class="(?:record|wlt)"[^>]*>\s*
        (?P<wins>\d+)-(?P<losses>\d+)-(?P<ties>\d+)
    \s*</td>
    """,
    re.IGNORECASE | re.VERBOSE,
)


def parse_standings(html: str) -> List[Tuple[str, int, int, int]]:
    """Extract team standings from an NFL.com league page using regex.

    Returns a list of (team, wins, losses, ties).
    """
    standings: List[Tuple[str, int, int, int]] = []
    for match in STANDING_ROW_RE.finditer(html):
        team = match.group("team").strip()
        wins = int(match.group("wins"))
        losses = int(match.group("losses"))
        ties = int(match.group("ties"))
        standings.append((team, wins, losses, ties))
    return standings


# -------- Primary standings fetch (uses bs4 when available) --------

def fetch_league_standings(
    league_id: str, session: Optional[object] = None
) -> List[Dict[str, str]]:
    """Fetch standings table for the given league ID from NFL.com.

    Returns a list of dicts with keys:
    - team
    - wlt         (e.g., "7-2-0")
    - pct         (win% as string like "0.778")
    - pts_for     (may be blank if not present)
    - pts_against (may be blank if not present)
    """
    sess = session or requests
    if sess is None:  # pragma: no cover
        raise RuntimeError("The requests library is required to fetch league standings")

    url = f"https://fantasy.nfl.com/league/{league_id}"
    response = sess.get(url)
    response.raise_for_status()
    html = response.text

    # If BeautifulSoup is available, prefer it for richer fields (PF/PA, pct cells).
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        standings: List[Dict[str, str]] = []

        # Try the common standings table; be tolerant of class name drift.
        # NFL has historically used classes like tableType-team / hasGroups, but these can change.
        rows = soup.select("table tbody tr")
        for row in rows:
            # Helper that tries multiple selectors for the same semantic cell
            def pick_text(selectors: List[str]) -> str:
                for sel in selectors:
                    cell = row.select_one(sel)
                    if cell:
                        return cell.get_text(strip=True)
                return ""

            team = pick_text(["td.teamName", "td.team", "td.team-name", "td.name"])
            wlt = pick_text(["td.wlt", "td.record", "td.w-l-t", "td.wltRecord"])
            pct = pick_text(["td.pct", "td.winPct", "td.percentage"])
            pts_for = pick_text(["td.pts_for", "td.pf", "td.pointsFor"])
            pts_against = pick_text(["td.pts_against", "td.pa", "td.pointsAgainst"])

            # If W-L-T not explicitly present, try to reconstruct from text like "7-2-0" found anywhere in row.
            if not wlt:
                m = re.search(r"\b(\d+)-(\d+)-(\d+)\b", row.get_text(" ", strip=True))
                if m:
                    wlt = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

            # If pct missing but we have W-L-T, compute it.
            if not pct and wlt:
                try:
                    w, l, t = (int(x) for x in wlt.split("-"))
                    games = w + l + t
                    pct = f"{(w + 0.5 * t) / games:.3f}" if games else ""
                except Exception:
                    pct = pct or ""

            # Only accept rows that look like real team lines.
            if team and wlt:
                standings.append(
                    {
                        "team": team,
                        "wlt": wlt,
                        "pct": pct,
                        "pts_for": pts_for,
                        "pts_against": pts_against,
                    }
                )

        # If Soup path yielded usable rows, return them.
        if standings:
            return standings

    # Fallback: regex-based minimal parsing (team + W-L-T); compute pct; PF/PA blank.
    parsed = parse_standings(html)
    results: List[Dict[str, str]] = []
    for team, w, l, t in parsed:
        games = w + l + t
        pct = f"{(w + 0.5 * t) / games:.3f}" if games else ""
        results.append(
            {
                "team": team,
                "wlt": f"{w}-{l}-{t}",
                "pct": pct,
                "pts_for": "",
                "pts_against": "",
            }
        )
    return results
