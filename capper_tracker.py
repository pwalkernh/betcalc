import requests
import json
import re
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from webdriver_manager.firefox import GeckoDriverManager


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
    
    # Make dates timezone-aware if they aren't already
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    
    # Set up Firefox options for headless browsing
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # Use manually installed geckodriver in Docker, fallback to webdriver-manager
    if os.path.exists('/usr/local/bin/geckodriver'):
        service = Service('/usr/local/bin/geckodriver')
        print(f"Using manual geckodriver: /usr/local/bin/geckodriver")
    else:
        service = Service(GeckoDriverManager().install())
        print(f"Using webdriver-manager geckodriver")
    
    # Set up virtual display for headless Firefox in Docker
    if os.environ.get('DISPLAY') == ':99':
        try:
            import subprocess
            subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'])
            time.sleep(1)
        except:
            pass
    
    try:
        driver = webdriver.Firefox(service=service, options=firefox_options)
        print("✓ Firefox WebDriver initialized successfully")
    except Exception as e:
        print(f"Error initializing Firefox WebDriver: {e}")
        print(f"geckodriver path: {service.path}")
        print(f"Firefox options: {firefox_options.arguments}")
        raise
    
    try:
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Keep clicking "Load More Picks" until we have enough data or no more button
        max_clicks = 5  # Prevent infinite loops
        click_count = 0
        
        while click_count < max_clicks:
            try:
                # Check if we have enough date coverage by looking at the earliest pick date
                html_content = driver.page_source
                earliest_date = _get_earliest_pick_date(html_content)
                
                if earliest_date and earliest_date <= start_date:
                    print(f"✓ Date range covered. Earliest pick: {earliest_date}")
                    break
                
                button_xpath = "//button[.//span/span[text()='Load More Picks']]"
                
                button_found = False
                try:
                    load_more_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, button_xpath))
                    )
                    print(f"Found button with xpath: {button_xpath}")
                    
                    # Scroll to the button to make sure it's visible
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                    time.sleep(1)
                    
                    # Try clicking with JavaScript first, then regular click
                    try:
                        driver.execute_script("arguments[0].click();", load_more_button)
                    except:
                        load_more_button.click()

                    WebDriverWait(driver, 10).until_not(
                        EC.text_to_be_present_in_element((By.XPATH, button_xpath), "Load More Picks")
                    )

                    # Now Wait for it to change back to "Load More Picks" (content loaded)
                    WebDriverWait(driver, 10).until(
                        EC.text_to_be_present_in_element((By.XPATH, button_xpath), "Load More Picks")
                    )
                    
                    click_count += 1
                    print(f"Clicked 'Load More' button (attempt {click_count})")
                    time.sleep(3)  # Wait longer for content to load
                    button_found = True
                    
                except (TimeoutException, NoSuchElementException):
                    print("No 'Load More' button found - all data may be loaded")
                    break
                    try:
                        load_more_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//span/span[text()='Load More Picks']]"))
                            #EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"Found button with selector: {selector}")
                        
                        # Scroll to the button to make sure it's visible
                        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                        time.sleep(1)
                        
                        # Try clicking with JavaScript first, then regular click
                        try:
                            driver.execute_script("arguments[0].click();", load_more_button)
                        except:
                            load_more_button.click()
                        
                        click_count += 1
                        print(f"Clicked 'Load More' button (attempt {click_count})")
                        time.sleep(3)  # Wait longer for content to load
                        button_found = True
                        break
                        
                    except (TimeoutException, NoSuchElementException):
                        continue
                
                if not button_found:
                    print("No 'Load More' button found - all data may be loaded")
                    break
                
            except Exception as e:
                print(f"Error during load more process: {e}")
                break
        
        if click_count >= max_clicks:
            print(f"Reached maximum clicks ({max_clicks}) - stopping")
        
        return driver.page_source
        
    finally:
        driver.quit()


def _get_earliest_pick_date(html_content: str) -> Optional[datetime]:
    """Helper function to extract the earliest pick date from HTML content."""
    try:
        # Try to extract JSON data first
        json_data = extract_sportsline_json_data(html_content)
        if json_data:
            picks_data = json_data.get('props', {}).get('pageProps', {}).get('expertPicksContainerProps', {}).get('pastData', {})
            edges = picks_data.get('expertPicks', {}).get('edges', [])
            
            if edges:
                # Print number of picks
                print(f"Number of picks: {len(edges)}")

                dates = []
                for edge in edges:
                    scheduled_time = edge.get('node', {}).get('game', {}).get('scheduledTime')
                    if scheduled_time:
                        try:
                            date_obj = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                            dates.append(date_obj)
                        except:
                            continue
                
                if dates:
                    earliest = min(dates)
                    print(f"Earliest pick date: {earliest}")
                    return earliest
                else:
                    print("No valid dates found in picks")
            else:
                print("No edges found in picks data")
        else:
            print("No JSON data extracted")
    except Exception as e:
        print(f"Error extracting earliest date: {e}")
    
    # Fallback: look for date patterns in HTML
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\w+ \d{1,2}, \d{4}'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, html_content)
        if matches:
            try:
                # Try to parse the first match
                date_str = matches[-1]  # Get the last (potentially earliest) date
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    return datetime.strptime(date_str, '%m/%d/%Y')
            except:
                continue
    
    print("No dates found in HTML content")
    return None


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
    # Look for __NEXT_DATA__ script tag
    next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
    match = re.search(next_data_pattern, html_content, re.DOTALL)
    
    if match:
        try:
            json_str = match.group(1)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse __NEXT_DATA__ JSON: {e}", json_str, 0)
    
    # Look for window.__NEXT_DATA__ assignment
    next_data_window_pattern = r'window\.__NEXT_DATA__\s*=\s*({.*?});'
    match = re.search(next_data_window_pattern, html_content, re.DOTALL)
    
    if match:
        try:
            json_str = match.group(1)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse window.__NEXT_DATA__ JSON: {e}", json_str, 0)
    
    # Look for window.__APOLLO_STATE__ assignment
    apollo_pattern = r'window\.__APOLLO_STATE__\s*=\s*({.*?});'
    match = re.search(apollo_pattern, html_content, re.DOTALL)
    
    if match:
        try:
            json_str = match.group(1)
            apollo_data = json.loads(json_str)
            # Wrap Apollo state in a structure similar to Next.js data
            return {"props": {"pageProps": {"apolloState": apollo_data}}}
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse __APOLLO_STATE__ JSON: {e}", json_str, 0)
    
    raise ValueError("No JSON data found in HTML content")


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
    def get_nested_value(data: Dict[str, Any], key_path: str) -> Any:
        """Helper function to get nested dictionary values using dot notation."""
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    try:
        # Navigate to the picks data
        page_props = json_data.get('props', {}).get('pageProps', {})
        picks_container = page_props.get('expertPicksContainerProps', {}).get('pastData', {})
        expert_picks = picks_container.get('expertPicks', {})
        edges = expert_picks.get('edges', [])
        
        if not edges:
            # Try alternative path for Apollo state
            apollo_state = page_props.get('apolloState', {})
            if apollo_state:
                # Look for picks in Apollo state structure
                for key, value in apollo_state.items():
                    if isinstance(value, dict) and 'edges' in value:
                        edges = value['edges']
                        break
        
        if not edges:
            raise ValueError("No picks data found in JSON structure")
        
        transformed_data = []
        
        for edge in edges:
            pick_data = {}
            
            # Extract each field using the mapping
            for json_key, output_key in fields_to_extract.items():
                value = get_nested_value(edge, json_key)
                pick_data[output_key] = value
            
            # Only add picks that have essential data
            if pick_data.get('resultStatus') and pick_data.get('game.scheduledTime'):
                transformed_data.append(pick_data)
        
        return transformed_data
        
    except Exception as e:
        raise ValueError(f"Failed to transform JSON data: {e}")

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
        raise ValueError("bet_data cannot be empty")
    
    wins = 0
    losses = 0
    draws = 0  # Push and Void outcomes
    total_units = 0.0
    net_results = 0.0
    
    for bet in bet_data:
        result_status = bet.get('resultStatus')
        unit_size = bet.get('unit', 1.0)  # Default to 1 unit if not specified
        odds = bet.get('selection.odds', -110)  # Default to -110 if not specified
        
        if result_status is None:
            continue
            
        # Convert unit size to float if it's a string
        if isinstance(unit_size, str):
            try:
                unit_size = float(unit_size)
            except ValueError:
                unit_size = 1.0
        
        # Convert odds to int if it's a string
        if isinstance(odds, str):
            try:
                odds = int(odds)
            except ValueError:
                odds = -110
        
        total_units += unit_size
        
        if result_status.lower() == 'win':
            wins += 1
            # Calculate winnings based on odds
            if odds > 0:
                # Positive odds: win amount = (odds / 100) * stake
                winnings = (odds / 100) * unit_size
            else:
                # Negative odds: win amount = (100 / abs(odds)) * stake
                winnings = (100 / abs(odds)) * unit_size
            net_results += winnings
            
        elif result_status.lower() == 'loss':
            losses += 1
            # Lose the stake
            net_results -= unit_size
            
        elif result_status.lower() in ['push', 'void']:
            draws += 1
            # No money won or lost, but still counts toward total units
            pass
    
    # Calculate ROI
    roi = (net_results / total_units) if total_units > 0 else 0.0
    
    return {
        "record": {
            "wins": wins,
            "losses": losses,
            "draws": draws
        },
        "results": net_results,
        "total_units": total_units,
        "roi": roi
    }
