"""Streamlit app for exploring NFL.com fantasy leagues."""
import streamlit as st

from league_api import fetch_league_data


def main() -> None:
    st.title("Fantasy Football Dashboard")
    league_id = st.text_input("Enter NFL.com league ID")
    if league_id:
        try:
            data = fetch_league_data(league_id)
            st.subheader("League Data")
            st.json(data)
        except Exception as exc:  # pragma: no cover - network errors
            st.error(f"Failed to load league data: {exc}")


if __name__ == "__main__":
    main()
