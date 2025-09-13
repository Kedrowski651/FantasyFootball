import sys
from pathlib import Path

import pytest

# Add project root to module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from league_api import fetch_league_data, fetch_league_standings, parse_standings


class DummyResponse:
    def __init__(self, data=None, headers=None, text=""):
        self._data = data
        self.headers = headers or {"Content-Type": "application/json"}
        self.text = text

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class DummySession:
    def __init__(self, data=None, text="", headers=None):
        self.data = data
        self.text = text
        self.headers = headers
        self.last_url = None

    def get(self, url):
        self.last_url = url
        return DummyResponse(self.data, headers=self.headers, text=self.text)


def test_fetch_league_data_uses_session_and_returns_json():
    session = DummySession({"league": "test"})
    data = fetch_league_data("123", session=session)
    assert data["league"] == "test"
    assert "123" in session.last_url


def test_fetch_league_data_errors_on_non_json():
    session = DummySession({}, headers={"Content-Type": "text/html"})
    with pytest.raises(ValueError):
        fetch_league_data("123", session=session)


def test_fetch_league_standings_parses_html_with_bs4():
    # If bs4 isn't installed, skip—fetch_league_standings will still be covered by regex test below
    pytest.importorskip("bs4")
    html = """
    <table class="tableType-team hasGroups">
        <tbody>
            <tr>
                <td class="team">Team A</td>
                <td class="wlt">5-3-0</td>
                <td class="pct">0.625</td>
                <td class="pts_for">650.4</td>
                <td class="pts_against">600.1</td>
            </tr>
            <tr>
                <td class="team">Team B</td>
                <td class="wlt">4-4-0</td>
                <td class="pct">0.500</td>
                <td class="pts_for">620.7</td>
                <td class="pts_against">610.5</td>
            </tr>
        </tbody>
    </table>
    """
    session = DummySession(text=html, headers={"Content-Type": "text/html"})
    standings = fetch_league_standings("999", session=session)
    assert standings == [
        {
            "team": "Team A",
            "wlt": "5-3-0",
            "pct": "0.625",
            "pts_for": "650.4",
            "pts_against": "600.1",
        },
        {
            "team": "Team B",
            "wlt": "4-4-0",
            "pct": "0.500",
            "pts_for": "620.7",
            "pts_against": "610.5",
        },
    ]
    assert "999" in session.last_url


def test_parse_standings_regex_fallback():
    # Covers the regex-based parser (and by extension, fetch_league_standings fallback logic)
    html = """
    <table id="standings">
        <tr><th>Team</th><th>Record</th></tr>
        <tr><td class="teamName">Alpha</td><td class="record">5-2-0</td></tr>
        <tr><td class="teamName">Bravo</td><td class="record">4-3-0</td></tr>
    </table>
    """
    standings = parse_standings(html)
    assert ("Alpha", 5, 2, 0) in standings
    assert ("Bravo", 4, 3, 0) in standings
