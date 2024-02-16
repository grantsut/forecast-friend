"""
Tests for tools that can be used by the agent.
"""

import json
import pytest
import requests

from src.tools import fred_series_search

# First patch calls to the FRED search API with requests so that it returns a list of prefetched results
# from a local JSON file.


@pytest.fixture
def mock_fred_search_good(monkeypatch):
    # Load presaved json response content from a search for "potato chips"
    with open("tests/fixtures/fred_chips_search_content.txt", mode="rb") as f:
        content = f.read()

    response = requests.models.Response()
    response._content = content
    response.status_code = 200

    # Patch requests.get() to return the response object
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)


# Test of the function fred_series_search
def test_fred_search(mock_fred_search_good):
    # Test that a search for "potato chips" returns results that can be parsed into a dict using json.loads
    response = fred_series_search(
        "potato chips", frequency="Monthly", return_fields=["popularity"]
    )
    results = json.loads(response)
    assert isinstance(results, dict)
    # The number of results should be greater than 0
    assert results["count"] > 0
    # The results json should contain a "series" field that is a list
    assert isinstance(results["series"], list)
    # The items in the "series" list should be dicts with the fields "title", "id", "frequency" and "popularity"
    assert all(
        isinstance(d, dict)
        and "popularity" in d
        and "title" in d
        and "id" in d
        and "frequency" in d
        for d in results["series"]
    )


# Create a fixture that patches requests.get() to return a bad response
@pytest.fixture
def mock_fred_search_fail(monkeypatch):
    # Create a response object that returns a resource not found error
    response = requests.models.Response()
    response.status_code = 404

    # Patch requests.get() to return the response object
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)


def test_fred_search_fail(mock_fred_search_fail):
    # Test that a search for "potato chips" returns an error message
    response = fred_series_search("potato chips")
    # The response should contain the string "fail"
    assert "fail" in response
    # The response should report the status code (404)
    assert "404" in response
