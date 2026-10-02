"""EcoCal Dashboard -- browse/filter the world economic calendar.

Local-only Streamlit app on top of the ecocal package. See README.md and
data.py for the real (ground-truthed, not README-assumed) ecocal API notes.
"""

from __future__ import annotations

import datetime as dt

import streamlit as st

from data import fetch_calendar, fetch_event_details

st.set_page_config(page_title="EcoCal Dashboard", layout="wide")
st.title("EcoCal Dashboard")

# --- Sidebar: date range + filters -----------------------------------------
today = dt.date.today()
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(today, today + dt.timedelta(days=7)),
    )
    if len(date_range) != 2:
        st.stop()
    start_date, end_date = date_range

try:
    calendar_df = fetch_calendar(start_date.isoformat(), end_date.isoformat())
except Exception as exc:  # noqa: BLE001 -- surfaced to the user, not swallowed
    st.error(f"Could not fetch the calendar: {exc}")
    st.stop()

with st.sidebar:
    impact_options = sorted(calendar_df["Impact"].dropna().unique())
    selected_impacts = st.multiselect("Impact", impact_options, default=impact_options)

    currency_options = sorted(calendar_df["Currency"].dropna().unique())
    selected_currencies = st.multiselect(
        "Currency", currency_options, default=currency_options
    )

filtered_df = calendar_df[
    calendar_df["Impact"].isin(selected_impacts)
    & calendar_df["Currency"].isin(selected_currencies)
]

st.caption(f"{len(filtered_df)} of {len(calendar_df)} events in range")

# --- Main table --------------------------------------------------------------
display_df = filtered_df[["Start", "Name", "Impact", "Currency"]]
selection = st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
)

# --- CSV export ---------------------------------------------------------------
st.download_button(
    "Export filtered view to CSV",
    data=display_df.to_csv(index=False).encode("utf-8"),
    file_name=f"ecocal_{start_date}_{end_date}.csv",
    mime="text/csv",
)

# --- On-demand detail view -----------------------------------------------------
selected_rows = selection.selection.rows if selection and selection.selection else []
if selected_rows:
    selected_id = filtered_df.iloc[selected_rows[0]]["Id"]
    st.subheader(filtered_df.iloc[selected_rows[0]]["Name"])
    try:
        details = fetch_event_details(selected_id)
    except Exception as exc:  # noqa: BLE001 -- surfaced to the user, not swallowed
        st.error(f"Could not fetch details for this event: {exc}")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Actual", details.get("actual"))
        col2.metric("Consensus", details.get("consensus"))
        col3.metric("Previous", details.get("previous"))

        st.write(f"**Country:** {details.get('countryCode', 'n/a')}")
        category = details.get("category") or {}
        st.write(f"**Category:** {category.get('name', 'n/a')}")
        st.write(f"**Source:** {details.get('source', 'n/a')}")
        if details.get("description"):
            st.markdown(details["description"], unsafe_allow_html=True)
else:
    st.info("Select a row in the table above to view its full details.")
