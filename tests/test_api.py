import unittest
import json
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

class TestBettingCalculatorAPI(unittest.TestCase):
    """Test cases for the Sports Betting Calculator API endpoints."""
    
    def setUp(self):
        """Set up test client before each test."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home(self):
        """Test the home endpoint."""
        response = self.app.get('/')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        self.assertIn('usage', data)
    
    def check_result_keys(self, result, keys={"odds", "stake", "payout", "profit"}):
        """Check that the result has the expected keys."""
        self.assertEqual(result.keys(), keys)

    def test_calculate_payout_positive_odds(self):
        """Test payout calculation with positive odds using both GET and POST."""
        payload = {
            "odds": "+150",
            "stake": 100
        }
        
        # Test POST method
        response = self.app.post('/calculate/payout', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertEqual(data["payout"], 250.0)
        self.assertEqual(data["profit"], 150.0)
        
        # Test GET method with same parameters
        response = self.app.get('/calculate/payout?odds=+150&stake=100')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertEqual(data["payout"], 250.0)
        self.assertEqual(data["profit"], 150.0)
    
    def test_calculate_payout_negative_odds(self):
        """Test payout calculation with negative odds."""
        payload = {
            "odds": "-200",
            "stake": 100
        }
        
        response = self.app.post('/calculate/payout', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertEqual(data["payout"], 150.0)
        self.assertEqual(data["profit"], 50.0)
    
    def test_calculate_payout_invalid_odds(self):
        """Test payout calculation with invalid odds."""

        for payload in [
            {"odds": "invalid", "stake": 100},
            {"odds": "+150", "stake": -50},
            {"odds": "+150", "stake": 0}
        ]:
            response = self.app.post('/calculate/payout', 
                                    json=payload,
                                    content_type='application/json')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", data)
    
    def test_calculate_stake_positive_odds(self):
        """Test stake calculation with positive odds using both GET and POST."""
        payload = {
            "odds": "+150",
            "payout": 250
        }
        
        # Test POST method
        response = self.app.post('/calculate/stake', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertAlmostEqual(data["stake"], 100.0, places=2)
        self.assertAlmostEqual(data["profit"], 150.0, places=2)
        self.assertAlmostEqual(data["payout"], 250.0, places=2)
        
        # Test GET method with same parameters
        response = self.app.get('/calculate/stake?odds=+150&payout=250')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertAlmostEqual(data["stake"], 100.0, places=2)
        self.assertAlmostEqual(data["profit"], 150.0, places=2)
        self.assertAlmostEqual(data["payout"], 250.0, places=2)
    
    def test_calculate_stake_negative_odds(self):
        """Test stake calculation with negative odds."""
        payload = {
            "odds": "-200",
            "payout": 150
        }
        
        response = self.app.post('/calculate/stake', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertAlmostEqual(data["stake"], 100.0, places=2)
        self.assertAlmostEqual(data["profit"], 50.0, places=2)
        self.assertAlmostEqual(data["payout"], 150.0, places=2)
    
    def test_calculate_stake_invalid_payout(self):
        """Test stake calculation with invalid payout."""

        for payload in [
            {"odds": "+150", "payout": -100},
            {"odds": "+150", "payout": 0}
        ]:
            response = self.app.post('/calculate/stake', 
                                    json=payload,
                                    content_type='application/json')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", data)
    
    def test_calculate_odds_positive_result(self):
        """Test odds calculation that results in positive odds using both GET and POST."""
        payload = {
            "stake": 100,
            "payout": 250
        }
        
        # Test POST method
        response = self.app.post('/calculate/odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertEqual(data["odds"], "+150")
        
        # Test GET method with same parameters
        response = self.app.get('/calculate/odds?stake=100&payout=250')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.check_result_keys(data)
        self.assertEqual(data["odds"], "+150")
    
    def test_calculate_odds_negative_result(self):
        """Test odds calculation that results in negative odds."""
        payload = {
            "stake": 200,
            "payout": 300
        }
        
        response = self.app.post('/calculate/odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        self.check_result_keys(data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["odds"], "-200")
    
    def test_calculate_odds_invalid_inputs(self):
        """Test odds calculation with invalid inputs."""

        for payload in [
            {"stake": -50, "payout": 100},
            {"stake": 0, "payout": 100},
            {"stake": 100, "payout": -50},
            {"stake": 100, "payout": 100},
            {"stake": 100, "payout": 50}
        ]:
            
            response = self.app.post('/calculate/odds', 
                                    json=payload,
                                    content_type='application/json')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", data)
    
    def test_missing_parameters(self):
        """Test API responses when required parameters are missing."""
        # Missing odds parameter
        response = self.app.post('/calculate/payout', 
                                json={"stake": 100},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Missing stake parameter
        response = self.app.post('/calculate/payout', 
                                json={"odds": "+150"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Missing payout parameter
        response = self.app.post('/calculate/stake', 
                                json={"odds": "+150"},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Missing odds parameter
        response = self.app.post('/calculate/stake', 
                                json={"payout": 250},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Missing stake parameter
        response = self.app.post('/calculate/odds', 
                                json={"payout": 250},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Missing payout parameter
        response = self.app.post('/calculate/odds', 
                                json={"stake": 100},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_calculate_effective_odds_positive(self):
        """Test effective odds calculation with positive odds using both GET and POST."""
        payload = {
            "odds": "+150",
            "fee": 0.03
        }
        
        # Test POST method
        response = self.app.post('/calculate/effective_odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("effective_odds", data)
        # The effective odds should be less than the original odds due to the fee
        self.assertLess(float(data["effective_odds"].replace("+", "")), 150)
        
        # Test GET method with same parameters
        response = self.app.get('/calculate/effective_odds?odds=+150&fee=0.03')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("effective_odds", data)
        # The effective odds should be less than the original odds due to the fee
        self.assertLess(float(data["effective_odds"].replace("+", "")), 150)
    
    def test_calculate_effective_odds_negative(self):
        """Test effective odds calculation with negative odds."""
        payload = {
            "odds": "-200",
            "fee": 0.03
        }
        
        response = self.app.post('/calculate/effective_odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("effective_odds", data)
        # The effective odds should be less negative than the original odds due to the fee
        self.assertGreater(float(data["effective_odds"].replace("-", "")), 200)
    
    def test_calculate_effective_odds_default_fee(self):
        """Test effective odds calculation with default fee."""
        payload = {
            "odds": "+150"
        }
        
        response = self.app.post('/calculate/effective_odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("effective_odds", data)
    
    def test_calculate_effective_odds_invalid_inputs(self):
        """Test effective odds calculation with invalid inputs."""
        for payload in [
            {"odds": "invalid"},
            {"odds": "+150", "fee": 1.1},
            {"odds": "+150", "fee": "invalid"}
        ]:
            response = self.app.post('/calculate/effective_odds', 
                                    json=payload,
                                    content_type='application/json')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", data)
    
    def test_calculate_effective_odds_missing_odds(self):
        """Test effective odds calculation with missing odds parameter."""
        payload = {
            "fee": 0.03
        }
        
        response = self.app.post('/calculate/effective_odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
    
    def test_calculate_effective_odds_negative_fee(self):
        """Test effective odds calculation with negative fee."""
        payload = {
            "odds": "+100",
            "fee": -0.10
        }
        
        response = self.app.post('/calculate/effective_odds', 
                                json=payload,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("effective_odds", data)
        # The effective odds should be greater than the original odds due to the negative fee
        self.assertEqual(float(data["effective_odds"].replace("+", "")), 110)

    def test_invalid_endpoint_get(self):
        """Test invalid endpoint with GET method (should return 404)."""
        response = self.app.get('/invalid/endpoint')
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_endpoint_post(self):
        """Test invalid endpoint with POST method (should return 404)."""
        response = self.app.post('/invalid/endpoint')
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
