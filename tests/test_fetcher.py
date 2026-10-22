"""Tests for HTTP fetcher and file loader."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import requests

from src.fetcher import fetch_warnings


def test_fetch_from_local_file(tmp_path: Path) -> None:
    """Test loading valid warning list from local JSON file."""
    mock_data = [{"id": 1, "headline": "Test Alert"}]
    test_file = tmp_path / "warnings.json"
    test_file.write_text(json.dumps(mock_data), encoding="utf-8")

    result = fetch_warnings(source=test_file)
    assert result == mock_data


def test_fetch_from_nonexistent_local_file(tmp_path: Path) -> None:
    """Non-existent local file should return an empty list gracefully."""
    missing = tmp_path / "missing.json"
    result = fetch_warnings(source=missing)
    assert result == []


def test_fetch_from_invalid_json_file(tmp_path: Path) -> None:
    """Malformed local JSON should return an empty list gracefully."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not-valid-json", encoding="utf-8")
    result = fetch_warnings(source=bad_file)
    assert result == []


@patch("src.fetcher.requests.get")
def test_fetch_http_success(mock_get: MagicMock) -> None:
    """Test successful HTTP GET returning list."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = json.dumps([{"id": 42, "headline": "Test Warning"}])
    mock_resp.json.return_value = [{"id": 42, "headline": "Test Warning"}]
    mock_get.return_value = mock_resp

    result = fetch_warnings("https://example.com/warnings.json")
    assert len(result) == 1
    assert result[0]["id"] == 42


@patch("src.fetcher.requests.get")
def test_fetch_http_empty_response(mock_get: MagicMock) -> None:
    """Test empty HTTP response body returns empty list."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "   "
    mock_get.return_value = mock_resp

    result = fetch_warnings("https://example.com/warnings.json")
    assert result == []


@patch("src.fetcher.requests.get")
def test_fetch_http_timeout(mock_get: MagicMock) -> None:
    """Test timeout handling returns empty list without raising."""
    mock_get.side_effect = requests.exceptions.Timeout("Timed out")
    result = fetch_warnings("https://example.com/warnings.json")
    assert result == []


@patch("src.fetcher.requests.get")
def test_fetch_http_error_500(mock_get: MagicMock) -> None:
    """Test HTTP 500 error handling returns empty list."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
    mock_get.return_value = mock_resp

    result = fetch_warnings("https://example.com/warnings.json")
    assert result == []


@patch("src.fetcher.requests.get")
def test_fetch_http_connection_error(mock_get: MagicMock) -> None:
    """Test connection failure handling returns empty list."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
    result = fetch_warnings("https://example.com/warnings.json")
    assert result == []
