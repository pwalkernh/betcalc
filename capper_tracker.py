import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


def fetch_sportsline_expert_webpage(url: str) -> str:
    """
    Fetch HTML data for the given sportsline expert web page.
    See sample data in "tests/data/Matt Severance - Vegas Expert Picks - Severance Pays - SportsLine.com.html".
    
    Args:
        url (str): The URL to fetch data from
    
    Returns:
        str: HTML content of the web page
        
    Raises:
        requests.RequestException: If the HTTP request fails
    """
    # Implement web scraping logic to fetch HTML content
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }  # Mimic a browser to avoid potential blocking
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        return response.text
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch URL {url}: {e}")

def extract_sportsline_json_data(html_content: str) -> Dict[str, Any]:
    """
    Extract raw JSON data from a SportsLine expert webpage HTML content.
    Result data should look like app/tests/data/Matt_Severance_Sample.json.
    
    Args:
        html_content (str): HTML content from a SportsLine expert webpage
        
    Returns:
        Dict[str, Any]: Raw JSON data containing expert profile and picks information.
        Structure includes:
            - props.pageProps.expertProfile: Expert profile information
            - props.pageProps.expertPicksContainerProps: Current and past picks data
            - props.pageProps.hottestExperts: League-specific expert rankings
            
    Raises:
        ValueError: If no JSON data can be found in the HTML content
        json.JSONDecodeError: If the extracted JSON cannot be parsed
    """
    # Implement JSON extraction logic from HTML content
    # Look for patterns like:
    # - window.__APOLLO_STATE__ = {...}
    # - window.__NEXT_DATA__ = {...}
    # - <script id="__NEXT_DATA__" type="application/json">...</script>
    pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
    match = re.search(pattern, html_content, re.DOTALL)
    if not match:
        raise ValueError("No JSON data found in the HTML content")
    
    try:
        json_str = match.group(1).strip()
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to parse extracted JSON: {e}", json_str, 0)


# Data fields to extract from the "edges" array in SportsLine JSON.
# The dictionary keys are the JSON keys to extract, and the values are the keys to use in the output.
fields_to_extract = {
    "node.resultStatus": "resultStatus",
    "node.unit": "unit",
    
    "node.game.abbrev": "game.abbrev",
    "node.game.scheduledTime": "game.scheduledTime",
    "node.game.homeTeamScore": "game.homeTeamScore",
    "node.game.awayTeamScore": "game.awayTeamScore",
    "node.game.league.abbrev": "game.league.abbrev",

    "node.selection.label": "selection.label",
    "node.selection.marketType": "selection.marketType",
    "node.selection.odds": "selection.odds",
    "node.selection.unit": "selection.unit",
}


def transform_sportsline_json_data(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform raw JSON data from a SportsLine expert webpage into a simplified format.
    
    Example output:
    [
        {
            "resultStatus": "Loss",
            "unit": 0.5,
            "game.abbrev": "MLB_20250617_BOS@SEA",
            "game.scheduledTime": "2025-06-18T01:40:00.000Z",
            "game.homeTeamScore": 8,
            "game.awayTeamScore": 0,
            "game.league.abbrev": "MLB",
            "selection.label": "First 5 Innings - Total Runs Under 4.5 -152",
            "selection.marketType": "PROP",
            "selection.odds": -152,
            "selection.unit": 0.5
        },
        # ... more entries
    ]
    
    Args:
        json_data (Dict[str, Any]): Raw JSON data from SportsLine expert webpage
        
    Returns:
        List[Dict[str, Any]]: Simplified array of bet data objects
        
    Raises:
        KeyError: If required fields are missing from the JSON data
        ValueError: If the JSON data structure is invalid
    """
    # Implement transformation logic from raw JSON data
    transformed = []
    try:
        # Focus on past picks for completed results
        edges = json_data.get('props', {}).get('pageProps', {}).get('expertPicksContainerProps', {}).get('pastData', {}).get('expertPicks', {}).get('edges', [])
        if not edges:
            raise ValueError("Invalid JSON structure: No 'pastData.expertPicks.edges' found")
        
        for edge in edges:
            node = edge.get('node', {})
            bet = {}
            for json_key, output_key in fields_to_extract.items():
                # Handle nested keys like "node.game.abbrev"
                keys = json_key.split('.')
                value = node
                for k in keys:
                    if isinstance(value, dict):
                        value = value.get(k)
                    else:
                        value = None
                        break
                if value is not None:
                    # Type conversions for consistency (e.g., ensure odds/unit are numeric)
                    if 'odds' in json_key and isinstance(value, (int, float)):
                        bet[output_key] = int(value)  # Keep as int for odds
                    elif 'unit' in json_key and isinstance(value, (int, float)):
                        bet[output_key] = float(value)  # Ensure float for calculations
                    else:
                        bet[output_key] = value
            # Only add if all required fields are present and valid
            required_fields = ['resultStatus', 'unit', 'selection.odds']
            if all(field in bet for field in required_fields):
                transformed.append(bet)
            else:
                raise KeyError(f"Missing required fields in node: {required_fields}")
    except KeyError as e:
        raise KeyError(f"Required JSON structure missing: {e}")
    except Exception as e:
        raise ValueError(f"Invalid JSON data structure: {e}")
    
    return transformed

def compute_bet_results(bet_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute betting results based on wins and losses using a specified unit size.
    Uses simplified JSON data from transform_sportsline_json_data().
    
    Args:
        bet_data (List[Dict[str, Any]]): Array of bet data objects
    
    Returns:
        Dict[str, Any]: Object containing:
            - record: Dict with 'wins', 'losses', 'draws' counts
            - results: Net profit/loss expressed as +/- units
            - total_units: Total units wagered
            - roi: Return on investment percentage
            
    Raises:
        ValueError: If bet_data is empty or malformed
        KeyError: If required fields are missing from bet data
    """
    if not bet_data:
        raise ValueError("bet_data is empty or malformed")
    
    record = {"wins": 0, "losses": 0, "draws": 0}
    results = 0.0
    total_units = 0.0
    
    for bet in bet_data:
        required_fields = ['resultStatus', 'unit', 'selection.odds']
        if not all(field in bet for field in required_fields):
            raise KeyError(f"Missing required fields in bet: {required_fields}")
        
        status = bet['resultStatus']
        unit = bet['unit']
        odds = bet['selection.odds']
        
        # Validate types
        if not isinstance(unit, (int, float)) or not isinstance(odds, (int, float)):
            raise ValueError(f"Invalid unit or odds in bet: unit={unit}, odds={odds}")
        
        stake = 100.0 * unit  # $100 per unit
        total_units += stake
        
        if status == "Win":
            record["wins"] += 1
            if odds > 0:
                payout = stake * (odds / 100.0)
            else:
                payout = stake * (100.0 / abs(odds))
            results += payout
        elif status == "Loss":
            record["losses"] += 1
            results -= stake
        elif status in ("Push", "Void"):
            record["draws"] += 1
            # No change to results, but stake is still wagered
        else:
            raise ValueError(f"Unknown resultStatus: {status}")
    
    roi = (results / total_units) if total_units > 0 else 0.0
    
    return {
        "record": record,
        "results": results,
        "total_units": total_units,
        "roi": roi
    }
