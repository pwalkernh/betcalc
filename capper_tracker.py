import requests
import json
import re
import subprocess
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


def fetch_expert_picks(expert: str, leagues: Optional[str] = None, 
                                 after: Optional[str] = None, count: int = 10) -> Dict[str, Any]:
    """
    Fetch expert picks data by calling the bash script.
    
    Args:
        expert (str): The unique identifier for the expert (required)
        leagues (str, optional): Comma-separated list of leagues to filter by
        after (str, optional): Base64 encoded cursor for pagination
        count (int, optional): Number of picks to fetch (default: 10, max: 25)
        
    Returns:
        Dict[str, Any]: The expert picks data from the API
        
    Raises:
        ValueError: If required parameters are missing or invalid
        RuntimeError: If script execution fails
        json.JSONDecodeError: If the script returns invalid JSON
    """
    if not expert:
        raise ValueError("expert parameter is required")
    
    if count <= 0 or count > 25:
        raise ValueError("count must be greater than 0 and less than or equal to 25")
    
    # Build script arguments
    script_args = ['--expert', expert, '--count', str(count)]
    
    if leagues:
        script_args.extend(['--leagues', leagues])
    
    if after:
        script_args.extend(['--after', after])
    
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'fetch_sl_expert_json.sh')
    
    if not script_path:
        raise RuntimeError("Unable to locate the fetch_sl_expert_json.sh script from " + os.getcwd())
    
    # Make sure the script is executable
    try:
        os.chmod(script_path, 0o755)
    except OSError:
        # Script might not exist or permissions might not be changeable
        pass
    
    # Call the bash script
    try:
        result = subprocess.run(
            [script_path] + script_args,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Script execution failed with return code {result.returncode}: {result.stderr}")
        
        # Parse the JSON response from the script
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Script execution timed out")
    except FileNotFoundError:
        raise RuntimeError("Script not found")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON response from script: {str(e)}", result.stdout, 0)
    except Exception as e:
        raise RuntimeError(f"Script execution error: {str(e)}")

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
