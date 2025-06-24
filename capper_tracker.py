import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def fetch_sportsline_expert_webpage(url: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
    """
    Fetch HTML data for the given sportsline expert web page.
    See sample data in "tests/data/Matt Severance - Vegas Expert Picks - Severance Pays - SportsLine.com.html".
    Checks the date range of the betting data to be sure it covers the timeframe requested, and activates the "Load More Picks" button as needed.
    
    Args:
        url (str): The URL to fetch data from
        start_date (datetime, optional): Start date for filtering data. Defaults to 7 days ago.
        end_date (datetime, optional): End date for filtering data. Defaults to current date/time.
    
    Returns:
        str: HTML content of the web page
        
    Raises:
        requests.RequestException: If the HTTP request fails
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=7)
    if end_date is None:
        end_date = datetime.now()

    # Set up headless Chrome browser for dynamic loading
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        while True:
            # Attempt to find and parse dates from embedded JSON or HTML to check range
            html_content = driver.page_source
            try:
                json_data = extract_sportsline_json_data(html_content)  # Reuse the extraction function
                picks = json_data.get('props', {}).get('pageProps', {}).get('expertPicksContainerProps', {}).get('expertPicks', {}).get('edges', [])
                if picks:
                    oldest_pick_date = min(
                        datetime.fromisoformat(pick['node']['game']['scheduledTime'].replace('Z', '+00:00'))
                        for pick in picks if 'node' in pick and 'game' in pick['node'] and 'scheduledTime' in pick['node']['game']
                    )
                    if oldest_pick_date <= start_date:
                        break  # Date range covered
            except (ValueError, KeyError, IndexError):
                # Fallback: Look for date elements in HTML (e.g., class or data attributes for picks)
                date_elements = driver.find_elements(By.CSS_SELECTOR, '[data-date]')  # Adjust selector based on actual HTML
                if date_elements:
                    oldest_date_str = min(elem.get_attribute('data-date') for elem in date_elements)
                    oldest_pick_date = datetime.fromisoformat(oldest_date_str)
                    if oldest_pick_date <= start_date:
                        break

            # Try to click "Load More Picks" button
            try:
                load_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More Picks')]"))  # Adjust XPath as needed
                )
                load_more_button.click()
                time.sleep(2)  # Wait for content to load
            except (NoSuchElementException, TimeoutException):
                break  # No more button or timeout, assume all data loaded
        
        return driver.page_source
    except Exception as e:
        raise requests.RequestException(f"Failed to fetch or process webpage: {str(e)}")
    finally:
        driver.quit()


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
    # Search for common JSON script patterns
    patterns = [
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r'window\.__APOLLO_STATE__ = (.*?);',
        r'window\.__NEXT_DATA__ = (.*?);'
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Failed to parse extracted JSON: {str(e)}", json_str, 0)
    raise ValueError("No valid JSON data found in the HTML content")


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
        {
            "resultStatus": "Win",
            "unit": 1,
            "game.abbrev": "NHL_20250617_EDM@FLA",
            "game.scheduledTime": "2025-06-18T00:00:00.000Z",
            "game.homeTeamScore": 5,
            "game.awayTeamScore": 1,
            "game.league.abbrev": "NHL",
            "selection.label": "Florida -146",
            "selection.marketType": "MONEY_LINE",
            "selection.odds": -146,
            "selection.unit": 1
        }
    ]
    
    Args:
        json_data (Dict[str, Any]): Raw JSON data from SportsLine expert webpage
        
    Returns:
        List[Dict[str, Any]]: Simplified array of bet data objects
        
    Raises:
        KeyError: If required fields are missing from the JSON data
        ValueError: If the JSON data structure is invalid
    """
    def get_nested_value(data: Dict, keys: str) -> Any:
        """Helper to safely extract nested values like 'node.game.abbrev'."""
        parts = keys.split('.')
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    try:
        edges = json_data['props']['pageProps']['expertPicksContainerProps']['expertPicks']['edges']
        transformed = []
        for edge in edges:
            bet = {}
            for json_key, output_key in fields_to_extract.items():
                value = get_nested_value(edge, json_key)
                if value is not None:
                    bet[output_key] = value
            if bet:  # Only add if some data was extracted
                transformed.append(bet)
        return transformed
    except KeyError as e:
        raise KeyError(f"Required field missing in JSON data: {str(e)}")
    except Exception as e:
        raise ValueError(f"Invalid JSON data structure: {str(e)}")
    
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
        raise ValueError("bet_data is empty")
    
    record = {"wins": 0, "losses": 0, "ties": 0}
    results = 0.0
    total_units = 0.0
    
    for bet in bet_data:
        try:
            status = bet["resultStatus"]
            unit = float(bet["unit"])
            odds = float(bet.get("selection.odds", 0))  # Default to 0 if missing
            
            total_units += unit
            if status == "Win":
                record["wins"] += 1
                if odds > 0:
                    profit = unit * (odds / 100)
                elif odds < 0:
                    profit = unit * (100 / abs(odds))
                else:
                    profit = unit  # Even money
                results += profit
            elif status == "Loss":
                record["losses"] += 1
                results -= unit
            elif status in ["Push", "Void"]:
                record["ties"] += 1
                # No change to results
            else:
                raise ValueError(f"Unknown resultStatus: {status}")
        except KeyError as e:
            raise KeyError(f"Missing required field in bet data: {str(e)}")
    
    roi = (results / total_units) if total_units > 0 else 0.0
    return {
        "record": record,
        "results": results,
        "total_units": total_units,
        "roi": roi
    }
