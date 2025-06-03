import unittest
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calculator import calculate_payout, calculate_stake, calculate_odds, parse_american_odds, decimal_to_american_odds, calculate_effective_odds


class TestBettingCalculator(unittest.TestCase):
    """Unit tests for betting calculator functions."""

    def test_parse_american_odds_positive(self):
        """Test parsing positive American odds."""
        self.assertEqual(parse_american_odds("+150"), 2.5)  # 1 + 150/100
        self.assertEqual(parse_american_odds("+200"), 3.0)  # 1 + 200/100
        self.assertEqual(parse_american_odds("+100"), 2.0)  # 1 + 100/100

    def test_parse_american_odds_negative(self):
        """Test parsing negative American odds."""
        self.assertEqual(parse_american_odds("-200"), 1.5)  # 1 + 100/200
        self.assertAlmostEqual(parse_american_odds("-150"), 1.667, places=3)  # 1 + 100/150
        self.assertAlmostEqual(parse_american_odds("-110"), 1.909, places=3)  # 1 + 100/110

    def test_parse_american_odds_no_sign(self):
        """Test parsing odds without explicit sign."""
        self.assertEqual(parse_american_odds("150"), 2.5)
        self.assertEqual(parse_american_odds("200"), 3.0)

    def test_parse_american_odds_invalid(self):
        """Test parsing invalid odds."""
        with self.assertRaises(ValueError):
            parse_american_odds("invalid")
        with self.assertRaises(ValueError):
            parse_american_odds("")
        with self.assertRaises(ValueError):
            parse_american_odds("abc123")

    def test_decimal_to_american_odds(self):
        """Test converting decimal odds to American odds."""
        self.assertEqual(decimal_to_american_odds(2.5), "+150")
        self.assertEqual(decimal_to_american_odds(3.0), "+200")
        self.assertEqual(decimal_to_american_odds(2.0), "+100")
        self.assertEqual(decimal_to_american_odds(1.5), "-200")
        self.assertEqual(decimal_to_american_odds(1.667), "-150")

    def test_calculate_payout_positive_odds(self):
        """Test payout calculation with positive odds."""
        # +150 odds with $100 stake should return $250 total payout ($150 profit + $100 stake)
        result = calculate_payout("+150", 100)
        self.assertEqual(result["payout"], 250.0)
        self.assertEqual(result["profit"], 150.0)
        self.assertEqual(result["stake"], 100)
        self.assertEqual(result["odds"], "+150")

        # +200 odds with $50 stake should return $150 total payout ($100 profit + $50 stake)
        result = calculate_payout("+200", 50)
        self.assertEqual(result["payout"], 150.0)
        self.assertEqual(result["profit"], 100.0)
        self.assertEqual(result["stake"], 50)

    def test_calculate_payout_negative_odds(self):
        """Test payout calculation with negative odds."""
        # -200 odds with $200 stake should return $300 total payout ($100 profit + $200 stake)
        result = calculate_payout("-200", 200)
        self.assertEqual(result["payout"], 300.0)
        self.assertEqual(result["profit"], 100.0)
        self.assertEqual(result["stake"], 200)

        # -150 odds with $150 stake should return $250 total payout ($100 profit + $150 stake)
        result = calculate_payout("-150", 150)
        self.assertEqual(result["payout"], 250.0)
        self.assertEqual(result["profit"], 100.0)
        self.assertEqual(result["stake"], 150)

    def test_calculate_payout_edge_cases(self):
        """Test payout calculation edge cases."""
        # +100 odds (even money) with $100 stake
        result = calculate_payout("+100", 100)
        self.assertEqual(result["payout"], 200.0)
        self.assertEqual(result["profit"], 100.0)

        # Very small stake
        result = calculate_payout("+150", 1)
        self.assertEqual(result["payout"], 2.5)
        self.assertEqual(result["profit"], 1.5)

    def test_calculate_payout_invalid_inputs(self):
        """Test payout calculation with invalid inputs."""
        with self.assertRaises(ValueError):
            calculate_payout("+150", -50)  # Negative stake
        
        with self.assertRaises(ValueError):
            calculate_payout("+150", 0)  # Zero stake

    def test_calculate_stake_positive_odds(self):
        """Test stake calculation with positive odds."""
        # +150 odds, want $250 total payout, should need $100 stake
        result = calculate_stake("+150", 250)
        self.assertAlmostEqual(result["stake"], 100.0, places=2)
        self.assertEqual(result["profit"], 150.0)
        self.assertEqual(result["total_payout"], 250)
        self.assertEqual(result["odds"], "+150")

        # +200 odds, want $150 total payout, should need $50 stake
        result = calculate_stake("+200", 150)
        self.assertAlmostEqual(result["stake"], 50.0, places=2)
        self.assertEqual(result["profit"], 100.0)

    def test_calculate_stake_negative_odds(self):
        """Test stake calculation with negative odds."""
        # -200 odds, want $300 total payout, should need $200 stake
        result = calculate_stake("-200", 300)
        self.assertAlmostEqual(result["stake"], 200.0, places=2)
        self.assertEqual(result["profit"], 100.0)
        self.assertEqual(result["total_payout"], 300)

        # -150 odds, want $250 total payout, should need $150 stake
        result = calculate_stake("-150", 250)
        self.assertAlmostEqual(result["stake"], 150.0, places=2)
        self.assertEqual(result["profit"], 100.0)

    def test_calculate_stake_invalid_inputs(self):
        """Test stake calculation with invalid inputs."""
        with self.assertRaises(ValueError):
            calculate_stake("+150", -100)  # Negative payout
        
        with self.assertRaises(ValueError):
            calculate_stake("+150", 0)  # Zero payout

    def test_calculate_odds_positive_result(self):
        """Test odds calculation that results in positive odds."""
        # $100 stake, $250 total payout should give +150 odds
        result = calculate_odds(100, 250)
        self.assertEqual(result["odds"], "+150")
        self.assertEqual(result["stake"], 100)
        self.assertEqual(result["total_payout"], 250)
        self.assertEqual(result["profit"], 150)

        # $50 stake, $150 total payout should give +200 odds
        result = calculate_odds(50, 150)
        self.assertEqual(result["odds"], "+200")
        self.assertEqual(result["profit"], 100)

    def test_calculate_odds_negative_result(self):
        """Test odds calculation that results in negative odds."""
        # $200 stake, $300 total payout should give -200 odds
        result = calculate_odds(200, 300)
        self.assertEqual(result["odds"], "-200")
        self.assertEqual(result["stake"], 200)
        self.assertEqual(result["total_payout"], 300)
        self.assertEqual(result["profit"], 100)

        # $150 stake, $250 total payout should give -150 odds
        result = calculate_odds(150, 250)
        self.assertEqual(result["odds"], "-150")
        self.assertEqual(result["profit"], 100)

    def test_calculate_odds_even_money(self):
        """Test odds calculation for even money (+100)."""
        # $100 stake, $200 total payout should give +100 odds
        result = calculate_odds(100, 200)
        self.assertEqual(result["odds"], "+100")
        self.assertEqual(result["profit"], 100)

    def test_calculate_odds_invalid_inputs(self):
        """Test odds calculation with invalid inputs."""
        with self.assertRaises(ValueError):
            calculate_odds(-50, 100)  # Negative stake
        
        with self.assertRaises(ValueError):
            calculate_odds(0, 100)  # Zero stake

        with self.assertRaises(ValueError):
            calculate_odds(100, -50)  # Negative payout

        with self.assertRaises(ValueError):
            calculate_odds(100, 100)  # Payout equal to stake (no profit)

        with self.assertRaises(ValueError):
            calculate_odds(100, 50)  # Payout less than stake

    def test_calculate_odds_rounding(self):
        """Test that odds calculation handles rounding properly."""
        # Test case that might result in fractional odds
        result = calculate_odds(100, 233.33)
        # Should round to nearest whole number for American odds
        self.assertIn(result["odds"], ["+133", "+134"])

    def calculate_effective_odds_for_comparison(self, odds_string, fee=0.03):
        """Calculate the effective odds for comparison purposes."""
        stake = 100 # Arbitrary stake, doesn't matter to the result
        decimal_odds = parse_american_odds(odds_string)
        total_payout = stake * decimal_odds
        profit = total_payout - stake
        adjusted_profit = profit * (1 - fee)
        adjusted_payout = stake + adjusted_profit
        result = calculate_odds(stake, adjusted_payout)
        return result['odds']

    def test_calculate_adjusted_odds(self):
        """Test adjusted odds calculation."""
        # Compute the result in an inefficient way to ensure the function is correct.
        self.assertEqual(calculate_effective_odds("-105"), self.calculate_effective_odds_for_comparison("-105"))
        self.assertEqual(calculate_effective_odds("+125"), self.calculate_effective_odds_for_comparison("+125"))

if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 