import os
import json
import requests
import streamlit as st


def fred_series_search(
    search_text: str,
    frequency: str | None = None,
    return_fields: list[str] | None = None,
    debug = False
) -> str:
    """
    Submits a query to the FRED search API and returns results as a serialized JSON.

    Args:
        search_text (str): space-separated terms to search for in series titles, units, frequencies and tags.
        frequency (str, optional): Optional frequency filter of the data, e.g. "Monthly", "Annual", "Daily".
        return_fields (list[str], optional): Optional additional fields to return in addition to the series title, ID
        frequency and last_updated. Options are: 'realtime_start', 'realtime_end', 'observation_start', 'observation_end',
        'frequency_short', 'units', 'units_short', 'seasonal_adjustment', 'seasonal_adjustment_short', 'popularity',
        'group_popularity', 'notes'.
    """
    params = {
        "file_type": "json",
        "api_key": st.secrets["FRED_API_KEY"],
        "search_text": search_text,
        "limit": 25,
    }

    fields = ["title", "id", "frequency", "last_updated"]
    if return_fields:
        fields.extend(return_fields)

    if frequency:
        params = params | {
            "filter_variable": "frequency",
            "filter_value": frequency,
        }

    r = requests.get(
        "https://api.stlouisfed.org/fred/series/search",
        params=params,
        timeout=10,
    )
    if r.status_code == 200:
        j = r.json()
        count = j["count"]
        series = [
            {f: d[f] for f in fields}
            for d in j["seriess"]
            if int(d["last_updated"][:4]) > 2022
        ]
        results = {"count": count, "series": series}
        return json.dumps(results)
    else:
        if debug:
            return r
        
        return f"Call to API failed with status code {r.status_code}."
