"""HTTP fetcher with timeout, retry, and error handling for Met Éireann open data."""

import json
import logging
from pathlib import Path
from typing import Any, List, Optional, Union
import requests

from src.config import DEFAULT_REQUEST_TIMEOUT, MET_EIREANN_WARNINGS_URL, USER_AGENT

logger = logging.getLogger(__name__)


def fetch_warnings(
    source: Optional[Union[str, Path]] = None,
    timeout: int = DEFAULT_REQUEST_TIMEOUT,
) -> List[dict[str, Any]]:
    """Fetch warnings from Met Éireann API endpoint or a local JSON file path.

    Args:
        source: URL or local file path. If None, uses MET_EIREANN_WARNINGS_URL.
        timeout: Request timeout in seconds.

    Returns:
        List of warning dictionaries. Returns an empty list on failure or empty feed.
    """
    target = source or MET_EIREANN_WARNINGS_URL

    # Support local file path for testing and dry-run
    if isinstance(target, Path) or (isinstance(target, str) and not target.startswith(("http://", "https://"))):
        file_path = Path(target)
        if not file_path.exists():
            logger.error("Local warnings file does not exist: %s", file_path)
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                logger.warning("Local file JSON root is not a list: %s", type(data))
                return []
        except Exception as exc:
            logger.error("Failed to read local warnings file %s: %s", file_path, exc)
            return []

    # Fetch from remote HTTP URL
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    try:
        logger.info("Fetching Met Éireann warnings from %s", target)
        response = requests.get(target, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Handle empty response body
        text = response.text.strip()
        if not text:
            logger.info("Received empty response body from warnings endpoint.")
            return []

        data = response.json()
        if isinstance(data, list):
            logger.info("Successfully fetched %d warning(s).", len(data))
            return data
        elif isinstance(data, dict):
            # In case the endpoint ever wraps alerts in a dict key (e.g., {"warnings": [...]})
            for key in ("warnings", "alerts", "items", "data"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            logger.warning("Received JSON object without recognized warning list key: %s", list(data.keys()))
            return []
        else:
            logger.warning("Unexpected JSON root type: %s", type(data))
            return []

    except requests.exceptions.Timeout:
        logger.warning("Request timed out while connecting to %s after %d seconds.", target, timeout)
        return []
    except requests.exceptions.HTTPError as http_err:
        logger.warning("HTTP error occurred when fetching warnings: %s", http_err)
        return []
    except requests.exceptions.RequestException as req_err:
        logger.warning("Network error occurred when fetching warnings: %s", req_err)
        return []
    except json.JSONDecodeError as json_err:
        logger.warning("Failed to parse JSON response from warnings endpoint: %s", json_err)
        return []
    except Exception as exc:
        logger.error("Unexpected error fetching warnings: %s", exc, exc_info=True)
        return []
