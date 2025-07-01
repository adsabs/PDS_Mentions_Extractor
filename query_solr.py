"""Module for querying the NASA ADS Solr API.

This module provides functions to interact with the NASA ADS Solr API, including
proper error handling and response validation.
"""

from typing import Dict, Any
import os
from pathlib import Path
import requests
from urllib.parse import urlencode
import logging
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a session with retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504],  # retry on these status codes
    allowed_methods=["GET"]  # only retry on GET requests
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def get_api_token() -> str:
    """Get the API token from the local config file.
    
    Returns:
        str: The API token
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the token is empty or invalid
    """
    config_path = Path('local_config_jarmak.py')
    if not config_path.exists():
        raise FileNotFoundError("API token config file not found")
        
    with open(config_path) as f:
        token = f.readline().strip()
        
    if not token or len(token) < 10:  # Basic validation
        raise ValueError("Invalid API token format")
        
    return token

def query_solr(query_params: Dict[str, Any]) -> requests.Response:
    """Query the NASA ADS Solr API with the given parameters.
    
    Args:
        query_params: Dictionary of query parameters to send to the API
        
    Returns:
        requests.Response: The API response object
        
    Raises:
        requests.exceptions.RequestException: If there's a network error
        requests.exceptions.HTTPError: If the API returns an error status code
        ValueError: If the API token is invalid
    """
    try:
        token = get_api_token()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to get API token: {e}")
        raise
        
    encoded_query = urlencode(query_params)
    url = f"https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}"
    
    try:
        # Use longer timeouts for connect and read operations
        response = session.get(
            url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=(10, 60)  # (connect timeout, read timeout)
        )
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Check if response is valid JSON
        try:
            response.json()
        except ValueError as e:
            logger.error(f"Invalid JSON response from API: {e}")
            raise requests.exceptions.HTTPError("Invalid JSON response from API")
            
        return response
        
    except requests.exceptions.Timeout as e:
        if isinstance(e, requests.exceptions.ConnectTimeout):
            logger.error("Connection to API timed out")
        else:
            logger.error("API request timed out - response took too long")
        raise
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.error("Invalid API token")
            raise ValueError("Invalid API token") from e
        elif e.response.status_code == 429:
            logger.error("API rate limit exceeded")
            raise
        else:
            logger.error(f"API request failed with status {e.response.status_code}: {e.response.text}")
            raise
    except RequestException as e:
        logger.error(f"Network error during API request: {e}")
        raise