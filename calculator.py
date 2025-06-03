def parse_american_odds(odds_string):
    """
    Parse American odds string and convert to decimal odds.
    
    Args:
        odds_string (str): American odds string (e.g., "+150", "-200")
        
    Returns:
        float: Decimal odds equivalent
        
    Raises:
        ValueError: If the odds string is invalid
    """
    if not odds_string or not isinstance(odds_string, str):
        raise ValueError("Odds must be a non-empty string")
    
    odds_string = odds_string.strip()
    
    if odds_string[0] == '+':
        # Positive American odds (underdog): +150 means bet 100 to win 150
        try:
            value = float(odds_string[1:])
            if value <= 0:
                raise ValueError("Positive odds must have a value greater than zero")
            return 1 + (value / 100)
        except ValueError:
            raise ValueError(f"Invalid positive American odds format: {odds_string}")
    
    elif odds_string[0] == '-':
        # Negative American odds (favorite): -200 means bet 200 to win 100
        try:
            value = float(odds_string[1:])
            if value <= 0:
                raise ValueError("Negative odds must have a value greater than zero")
            return 1 + (100 / value)
        except ValueError:
            raise ValueError(f"Invalid negative American odds format: {odds_string}")
    
    else:
        # Try to interpret as a number if no sign
        try:
            value = float(odds_string)
            if value > 0:
                return 1 + (value / 100)  # Treat as positive odds
            else:
                raise ValueError("Odds without sign must be positive")
        except ValueError:
            raise ValueError(f"Invalid American odds format: {odds_string}")


def decimal_to_american_odds(decimal_odds):
    """
    Convert decimal odds to American odds string.
    
    Args:
        decimal_odds (float): Decimal odds value
        
    Returns:
        str: American odds string
    """
    # As the unit stake is always included, decimal odds always have a value greater than 1.
    if decimal_odds < 1:
        raise ValueError("Decimal odds must be 1.0 or greater")
    
    if decimal_odds == 1:
        return "Undefined"
    
    if decimal_odds >= 2.0:
        # Positive American odds
        american = (decimal_odds - 1) * 100
        return f"+{int(american)}"
    else:
        # Negative American odds
        american = round(100.0 / float(decimal_odds - 1))
        return f"-{int(american)}"


def calculate_payout(odds_string, stake):
    """
    Calculate the potential payout for a bet given the odds and stake.
    
    Args:
        odds_string (str): American odds string (e.g., "+150", "-200")
        stake (float): Amount wagered in dollars
        
    Returns:
        dict: Dictionary containing payout details
            - payout (float): Total payout including stake
            - profit (float): Profit amount (payout - stake)
            - stake (float): Original stake
            - odds (str): Original odds string
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not isinstance(stake, (int, float)):
        raise ValueError("Stake must be a number")
    
    if stake <= 0:
        raise ValueError("Stake must be greater than zero")
    
    # Parse odds and calculate payout
    decimal_odds = parse_american_odds(odds_string)
    total_payout = stake * decimal_odds
    profit = total_payout - stake
    
    return {
        "payout": round(total_payout, 2),
        "profit": round(profit, 2),
        "stake": stake,
        "odds": odds_string
    }


def calculate_stake(odds_string, desired_payout):
    """
    Calculate the stake required to achieve a desired payout at given odds.
    
    Args:
        odds_string (str): American odds string (e.g., "+150", "-200")
        desired_payout (float): Desired total payout in dollars
        
    Returns:
        dict: Dictionary containing stake calculation details
            - stake (float): Required stake amount
            - profit (float): Expected profit
            - total_payout (float): Total payout (same as desired_payout)
            - odds (str): Original odds string
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not isinstance(desired_payout, (int, float)):
        raise ValueError("Payout must be a number")
    
    if desired_payout <= 0:
        raise ValueError("Payout must be greater than zero")
    
    # Parse odds and calculate stake
    decimal_odds = parse_american_odds(odds_string)
    required_stake = desired_payout / decimal_odds
    profit = desired_payout - required_stake
    
    return {
        "stake": round(required_stake, 2),
        "profit": round(profit, 2),
        "total_payout": desired_payout,
        "odds": odds_string
    }


def calculate_odds(stake, desired_payout):
    """
    Calculate the odds required to achieve a desired payout with a given stake.
    
    Args:
        stake (float): Amount to be wagered in dollars
        desired_payout (float): Desired total payout in dollars
        
    Returns:
        dict: Dictionary containing odds calculation details
            - odds (str): American odds string
            - decimal_odds (float): Decimal odds value
            - stake (float): Original stake
            - total_payout (float): Total payout
            - profit (float): Expected profit
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not isinstance(stake, (int, float)):
        raise ValueError("Stake must be a number")
    
    if not isinstance(desired_payout, (int, float)):
        raise ValueError("Payout must be a number")
    
    if stake <= 0:
        raise ValueError("Stake must be greater than zero")
    
    if desired_payout <= 0:
        raise ValueError("Payout must be greater than zero")
    
    if desired_payout <= stake:
        raise ValueError("Payout must be greater than stake for a winning bet")
    
    # Calculate decimal odds and convert to American
    decimal_odds = desired_payout / float(stake)
    american_odds = decimal_to_american_odds(decimal_odds)
    profit = desired_payout - stake
    
    return {
        "odds": american_odds,
        "decimal_odds": round(decimal_odds, 4),
        "stake": stake,
        "total_payout": desired_payout,
        "profit": round(profit, 2)
    }

# TODO: Implement this.  Function stub added to allow writing unit tests.
def calculate_effective_odds(odds_string, fee=0.03):
    pass

def calculate_effective_odds(odds_string, fee=0.03):
    """
    Calculate the effective odds after accounting for a fee on profits.
    
    Args:
        odds_string (str): American odds string (e.g., "+150", "-200")
        fee (float): Fee percentage as a decimal (default: 0.03 for 3%)
        
    Returns:
        str: Effective American odds string after fee adjustment
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not isinstance(fee, (int, float)):
        raise ValueError("Fee must be a number")
    
    if fee < 0 or fee >= 1:
        raise ValueError("Fee must be between 0 and 1")
    
    # Parse the original odds to decimal
    decimal_odds = parse_american_odds(odds_string)
    
    # Calculate the profit factor (1 - fee)
    profit_factor = 1 - fee
    
    # In decimal odds, the profit component is (decimal_odds - 1)
    # We adjust this profit component by the profit factor
    adjusted_profit = (decimal_odds - 1) * profit_factor
    
    # The new effective decimal odds
    effective_decimal_odds = 1 + adjusted_profit
    
    # Convert back to American odds
    return decimal_to_american_odds(effective_decimal_odds)
