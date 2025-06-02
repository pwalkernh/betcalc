import requests
import json

# Base URL of the API (change if running on a different host/port)
BASE_URL = "http://localhost:5000"

def test_calculate_payout():
    """Test the payout calculation endpoint."""
    print("\n=== Testing Calculate Payout ===")
    
    # Test case 1: Positive odds
    payload = {
        "odds": "+150",
        "stake": 100
    }
    
    response = requests.post(f"{BASE_URL}/calculate/payout", json=payload)
    print(f"POST {BASE_URL}/calculate/payout")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    
    # Test case 2: Negative odds
    payload = {
        "odds": "-200",
        "stake": 100
    }
    
    response = requests.post(f"{BASE_URL}/calculate/payout", json=payload)
    print(f"POST {BASE_URL}/calculate/payout")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    
    # Test case 3: Error case - invalid odds
    payload = {
        "odds": "invalid",
        "stake": 100
    }
    
    response = requests.post(f"{BASE_URL}/calculate/payout", json=payload)
    print(f"POST {BASE_URL}/calculate/payout (Error case)")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")

def test_calculate_stake():
    """Test the stake calculation endpoint."""
    print("\n=== Testing Calculate Stake ===")
    
    # Test case 1: Positive odds
    payload = {
        "odds": "+150",
        "payout": 250
    }
    
    response = requests.post(f"{BASE_URL}/calculate/stake", json=payload)
    print(f"POST {BASE_URL}/calculate/stake")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    
    # Test case 2: Negative odds
    payload = {
        "odds": "-200",
        "payout": 150
    }
    
    response = requests.post(f"{BASE_URL}/calculate/stake", json=payload)
    print(f"POST {BASE_URL}/calculate/stake")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    
    # Test case 3: Error case - negative payout
    payload = {
        "odds": "+150",
        "payout": -100
    }
    
    response = requests.post(f"{BASE_URL}/calculate/stake", json=payload)
    print(f"POST {BASE_URL}/calculate/stake (Error case)")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")

def test_calculate_odds():
    """Test the odds calculation endpoint."""
    print("\n=== Testing Calculate Odds ===")
    
    # Test case 1: Positive odds result
    payload = {
        "stake": 100,
        "payout": 250
    }
    
    response = requests.post(f"{BASE_URL}/calculate/odds", json=payload)
    print(f"POST {BASE_URL}/calculate/odds")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    
    # Test case 2: Negative odds result
    payload = {
        "stake": 200,
        "payout": 300
    }
    
    response = requests.post(f"{BASE_URL}/calculate/odds", json=payload)
    print(f"POST {BASE_URL}/calculate/odds")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    
    # Test case 3: Error case - payout <= stake
    payload = {
        "stake": 100,
        "payout": 100
    }
    
    response = requests.post(f"{BASE_URL}/calculate/odds", json=payload)
    print(f"POST {BASE_URL}/calculate/odds (Error case)")
    print(f"Request: {json.dumps(payload)}")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")

def test_home():
    """Test the home endpoint."""
    print("\n=== Testing Home Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"GET {BASE_URL}/")
    print(f"Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=== Sports Betting Calculator API Test ===")
    print(f"Testing API at {BASE_URL}")
    
    try:
        # Test home endpoint
        test_home()
        
        # Test all calculation endpoints
        test_calculate_payout()
        test_calculate_stake()
        test_calculate_odds()
        
        print("\n✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to the API at {BASE_URL}")
        print("   Make sure the API server is running.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}") 