import sys
from pathlib import Path

# Add project root to module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from league_api import fetch_league_data

class DummyResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

class DummySession:
    def __init__(self, data):
        self.data = data
        self.last_url = None
    def get(self, url):
        self.last_url = url
        return DummyResponse(self.data)

def test_fetch_league_data_uses_session_and_returns_json():
    session = DummySession({"league": "test"})
    data = fetch_league_data("123", session=session)
    assert data["league"] == "test"
    assert "123" in session.last_url
