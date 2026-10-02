"""Data access layer wrapping the ecocal package.

ecocal's installed code calls the removed `numpy.NaN` alias (NumPy 2.0
dropped it in favor of `numpy.nan`, the same value). Restoring the alias
here, before importing ecocal, is a contained, behavior-neutral workaround
-- see README.md for why a modern numpy/pandas is used instead of pinning
old enough to avoid this (that reintroduces a no-wheel-for-3.13 build
failure).
"""

from __future__ import annotations

import numpy as np

np.NaN = np.nan  # noqa: N816 -- restoring a removed numpy alias, not a new name

import pandas as pd
import requests
import streamlit as st
from ecocal import Calendar
from ecocal.constants import API_SOURCE_URL, BASE_URL, DEFAULT_USER_AGENT

# Real columns returned by Calendar.getCalendar(withDetails=False), confirmed
# by an actual live call (not assumed from ecocal's README, which is
# incomplete/inaccurate -- see the project's vault note). There is no
# "Country" column at the basic-table level; country only appears inside a
# single event's detail payload (as `countryCode`).
BASIC_COLUMNS = ["Id", "Start", "Name", "Impact", "Currency"]


@st.cache_data(show_spinner="Fetching economic calendar...")
def fetch_calendar(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch the basic calendar for a date range (YYYY-MM-DD strings).

    Deliberately withDetails=False -- per-event details are fetched
    on-demand (fetch_event_details) rather than eagerly for the whole
    range, since that fires one extra HTTP request per event against an
    undocumented third-party API.
    """
    cal = Calendar(
        startHorizon=start_date,
        endHorizon=end_date,
        withDetails=False,
        withProgressBar=False,
        nbThreads=10,
    )
    df = cal.getCalendar(withDetails=False).copy()
    df["Start"] = pd.to_datetime(df["Start"], format="%m/%d/%Y %H:%M:%S")
    return df.sort_values("Start").reset_index(drop=True)


@st.cache_data(show_spinner="Fetching event details...")
def fetch_event_details(event_id: str) -> dict:
    """Fetch full details for one event, on demand.

    Uses ecocal's public constants directly rather than its private
    Calendar._requestDetails method, so this doesn't depend on an
    internal implementation detail that could change without notice.
    """
    url = f"{API_SOURCE_URL}/{event_id}"
    response = requests.get(
        url=url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": BASE_URL,
            "Connection": "keep-alive",
            "User-Agent": DEFAULT_USER_AGENT,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
