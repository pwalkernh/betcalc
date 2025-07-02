from flask import Flask, request, jsonify
from calculator import calculate_payout, calculate_stake, calculate_odds, calculate_effective_odds

app = Flask(__name__)

@app.route('/calculate/payout', methods=['POST', 'GET'])
def get_payout():
    """
    Calculate the potential payout for a bet given the odds and stake.
    
    POST JSON Parameters:
        odds (str): American odds string (e.g., "+150", "-200")
        stake (float): Amount wagered in dollars
        
    GET Query Parameters:
        odds (str): American odds string (e.g., "+150", "-200")
        stake (float): Amount wagered in dollars
        
    Returns:
        JSON: {"payout": float, "profit": float, "stake": float, "odds": str} on success
        JSON: {"error": str} with appropriate status code on error
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate odds
            if 'odds' not in data:
                return jsonify({"error": "Missing 'odds' parameter"}), 400
            
            odds_string = data.get('odds')
            
            # Validate stake
            if 'stake' not in data:
                return jsonify({"error": "Missing 'stake' parameter"}), 400
            
            try:
                stake = float(data.get('stake'))
            except ValueError:
                return jsonify({"error": "Stake must be a valid number"}), 400
            
        elif request.method == 'GET':
            # Validate odds
            odds_string = request.args.get('odds')
            if not odds_string:
                return jsonify({"error": "Missing 'odds' parameter"}), 400
            
            # Validate stake
            stake_str = request.args.get('stake')
            if not stake_str:
                return jsonify({"error": "Missing 'stake' parameter"}), 400
            
            try:
                stake = float(stake_str)
            except ValueError:
                return jsonify({"error": "Stake must be a valid number"}), 400
        
        # Calculate payout using calculator function
        try:
            result = calculate_payout(odds_string, stake)
            return jsonify({
                "payout": result["payout"],
                "profit": result["profit"],
                "stake": result["stake"],
                "odds": result["odds"]
            })
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/calculate/stake', methods=['POST', 'GET'])
def get_stake():
    """
    Calculate the stake required to achieve a desired payout at given odds.
    
    POST JSON Parameters:
        odds (str): American odds string (e.g., "+150", "-200")
        payout (float): Desired total payout in dollars
        
    GET Query Parameters:
        odds (str): American odds string (e.g., "+150", "-200")
        payout (float): Desired total payout in dollars
        
    Returns:
        JSON: {"stake": float, "profit": float, "payout": float, "odds": str} on success
        JSON: {"error": str} with appropriate status code on error
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate odds
            if 'odds' not in data:
                return jsonify({"error": "Missing 'odds' parameter"}), 400
            
            odds_string = data.get('odds')
            
            # Validate payout
            if 'payout' not in data:
                return jsonify({"error": "Missing 'payout' parameter"}), 400
            
            try:
                payout = float(data.get('payout'))
            except ValueError:
                return jsonify({"error": "Payout must be a valid number"}), 400
            
            if payout <= 0:
                return jsonify({"error": "Payout must be greater than zero"}), 400
            
        elif request.method == 'GET':
            # Validate odds
            odds_string = request.args.get('odds')
            if not odds_string:
                return jsonify({"error": "Missing 'odds' parameter"}), 400
            
            # Validate payout
            payout_str = request.args.get('payout')
            if not payout_str:
                return jsonify({"error": "Missing 'payout' parameter"}), 400
            
            try:
                payout = float(payout_str)
            except ValueError:
                return jsonify({"error": "Payout must be a valid number"}), 400
            
            if payout <= 0:
                return jsonify({"error": "Payout must be greater than zero"}), 400
        
        # Calculate stake using calculator function
        try:
            result = calculate_stake(odds_string, payout)
            return jsonify({
                "stake": result["stake"],
                "profit": result["profit"],
                "payout": result["payout"],
                "odds": result["odds"]
            })
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/calculate/odds', methods=['POST', 'GET'])
def get_odds():
    """
    Calculate the odds required to achieve a desired payout with a given stake.
    
    POST JSON Parameters:
        stake (float): Amount to be wagered in dollars
        payout (float): Desired total payout in dollars
        
    GET Query Parameters:
        stake (float): Amount to be wagered in dollars
        payout (float): Desired total payout in dollars
        
    Returns:
        JSON: {"odds": str, "stake": float, "payout": float, "profit": float} on success
        JSON: {"error": str} with appropriate status code on error
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate stake
            if 'stake' not in data:
                return jsonify({"error": "Missing 'stake' parameter"}), 400
            
            try:
                stake = float(data.get('stake'))
            except ValueError:
                return jsonify({"error": "Stake must be a valid number"}), 400
            
            if stake <= 0:
                return jsonify({"error": "Stake must be greater than zero"}), 400
            
            # Validate payout
            if 'payout' not in data:
                return jsonify({"error": "Missing 'payout' parameter"}), 400
            
            try:
                payout = float(data.get('payout'))
            except ValueError:
                return jsonify({"error": "Payout must be a valid number"}), 400
            
            if payout <= stake:
                return jsonify({"error": "Payout must be greater than stake for a winning bet"}), 400
            
        elif request.method == 'GET':
            # Validate stake
            stake_str = request.args.get('stake')
            if not stake_str:
                return jsonify({"error": "Missing 'stake' parameter"}), 400
            
            try:
                stake = float(stake_str)
            except ValueError:
                return jsonify({"error": "Stake must be a valid number"}), 400
            
            if stake <= 0:
                return jsonify({"error": "Stake must be greater than zero"}), 400
            
            # Validate payout
            payout_str = request.args.get('payout')
            if not payout_str:
                return jsonify({"error": "Missing 'payout' parameter"}), 400
            
            try:
                payout = float(payout_str)
            except ValueError:
                return jsonify({"error": "Payout must be a valid number"}), 400
            
            if payout <= stake:
                return jsonify({"error": "Payout must be greater than stake for a winning bet"}), 400
        
        # Calculate odds using calculator function
        try:
            result = calculate_odds(stake, payout)
            return jsonify({
                "odds": result["odds"],
                "stake": result["stake"],
                "payout": result["payout"],
                "profit": result["profit"]
            })
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/calculate/effective_odds', methods=['POST', 'GET'])
def get_effective_odds():
    """
    Calculate the effective odds after adjusting for a percentage fee on the profit.
    
    POST JSON Parameters:
        odds (str): American odds string (e.g., "+150", "-200")
        fee (float, optional): Percentage fee on profit as a decimal (e.g., 0.03 for 3%, -0.03 for -3%). 
                              Defaults to 0.03. Must be less than 1.
                              Negative fees increase the effective odds, positive fees decrease them.
        
    GET Query Parameters:
        odds (str): American odds string (e.g., "+150", "-200")
        fee (float, optional): Percentage fee on profit as a decimal (e.g., 0.03 for 3%, -0.03 for -3%). 
                              Defaults to 0.03. Must be less than 1.
                              Negative fees increase the effective odds, positive fees decrease them.
        
    Returns:
        JSON: {"effective_odds": str} on success
        JSON: {"error": str} with appropriate status code on error
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate odds
            if 'odds' not in data:
                return jsonify({"error": "Missing 'odds' parameter"}), 400
            
            odds_string = data.get('odds')
            
            # Get fee if provided, otherwise use default
            fee = data.get('fee', 0.03)
            
        elif request.method == 'GET':
            # Validate odds
            odds_string = request.args.get('odds')
            if not odds_string:
                return jsonify({"error": "Missing 'odds' parameter"}), 400
            
            # Get fee if provided, otherwise use default
            fee_str = request.args.get('fee', '0.03')
            try:
                fee = float(fee_str)
            except ValueError:
                return jsonify({"error": "Fee must be a valid number"}), 400
        
        try:
            fee = float(fee)
        except ValueError:
            return jsonify({"error": "Fee must be a valid number"}), 400
        
        if fee >= 1:
            return jsonify({"error": "Fee must be < 1"}), 400
        
        # Calculate effective odds using calculator function
        try:
            effective_odds = calculate_effective_odds(odds_string, fee)
            return jsonify({
                "effective_odds": effective_odds
            })
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/')
def home():
    """Return API information and documentation."""
    return jsonify({
        "name": "Sports Betting Calculator API",
        "version": "1.0.0",
        "endpoints": {
            "/calculate/payout": "Calculate payout from odds and stake",
            "/calculate/stake": "Calculate stake from odds and payout",
            "/calculate/odds": "Calculate odds from stake and payout",
            "/calculate/effective_odds": "Calculate effective odds after fee adjustment"
        },
        "usage": "Send POST requests with JSON data to the endpoints"
    })

print("Starting the API...")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 