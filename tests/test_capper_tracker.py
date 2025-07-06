
import unittest
import json
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from capper_tracker import (
    fetch_expert_picks,
    transform_sportsline_json_data,
    compute_bet_results,
    fields_to_extract
)


class TestCapperTracker(unittest.TestCase):
    """Test cases for capper tracker functionality."""

    def setUp(self):
        """Set up test fixtures."""

        self.expectedSimplifiedJSON = [
            {
                "resultStatus":"Loss",
                "unit":1,
                "game.abbrev":"MLB_20250618_COL@WAS",
                "game.scheduledTime":"2025-06-19T00:30:00.000Z",
                "game.homeTeamScore":1,
                "game.awayTeamScore":3,
                "game.league.abbrev":"MLB",
                "selection.label":"Washington -158",
                "selection.marketType":"MONEY_LINE",
                "selection.odds":-158,
                "selection.unit":1
            },
            {
                "resultStatus":"Loss",
                "unit":0.25,
                "game.abbrev":"MLB_20250618_BOS@SEA",
                "game.scheduledTime":"2025-06-18T20:10:00.000Z",
                "game.homeTeamScore":1,
                "game.awayTeamScore":3,
                "game.league.abbrev":"MLB",
                "selection.label":"Seattle +1.5 -179",
                "selection.marketType":"POINT_SPREAD",
                "selection.odds":-179,
                "selection.unit":0.25
            },
            {
                "resultStatus":"Loss",
                "unit":0.5,
                "game.abbrev":"MLB_20250617_CLE@SF",
                "game.scheduledTime":"2025-06-18T01:45:00.000Z",
                "game.homeTeamScore":2,
                "game.awayTeamScore":3,
                "game.league.abbrev":"MLB",
                "selection.label":"San Francisco -160",
                "selection.marketType":"MONEY_LINE",
                "selection.odds":-160,
                "selection.unit":0.5
            },
            {
                "resultStatus":"Loss",
                "unit":0.5,
                "game.abbrev":"MLB_20250617_BOS@SEA",
                "game.scheduledTime":"2025-06-18T01:40:00.000Z",
                "game.homeTeamScore":8,
                "game.awayTeamScore":0,
                "game.league.abbrev":"MLB",
                "selection.label":"First 5 Innings - Total Runs Under 4.5 -152",
                "selection.marketType":"PROP",
                "selection.odds":-152,
                "selection.unit":0.5
            },
            {
                "resultStatus":"Win",
                "unit":0.5,
                "game.abbrev":"MLB_20250617_COL@WAS",
                "game.scheduledTime":"2025-06-17T22:45:00.000Z",
                "game.homeTeamScore":6,
                "game.awayTeamScore":10,
                "game.league.abbrev":"MLB",
                "selection.label":"Luis Garcia Under 1.5 Total Hits -165",
                "selection.marketType":"PROP",
                "selection.odds":-165,
                "selection.unit":0.5
            }
        ]        

    def test_transform_sportsline_json_data_with_sample_data(self):
        """Test basic functionality of transform_sportsline_json_data."""
        with open('tests/data/Expert_50774572_Next_5_MLB.json', 'r', encoding='utf-8') as f:
            sample_json = json.load(f)

        result = transform_sportsline_json_data(sample_json)
        # pretty print the result
        # print(json.dumps(result, indent=4))

        self.assertEqual(result, self.expectedSimplifiedJSON)

    def test_compute_bet_results_basic(self):
        """Test basic functionality of compute_bet_results."""
        sample_bet_data = [
            {
                "resultStatus": "Push",
                "unit": 0.25,
                "game.abbrev": "MLB_20250618_BOS@SEA",
                "game.scheduledTime": "2025-06-18T20:10:00.000Z",
                "game.homeTeamScore": 2,
                "game.awayTeamScore": 3,
                "game.league.abbrev": "MLB",
                "selection.label": "Seattle +1 -179",
                "selection.marketType": "POINT_SPREAD",
                "selection.odds": -179,
                "selection.unit": 0.25
            },
            {
                "resultStatus": "Win",
                "unit": 1.0,
                "game.abbrev": "MLB_20250617_BOS@SEA",
                "game.scheduledTime": "2025-06-18T01:40:00.000Z",
                "game.homeTeamScore": 5,
                "game.awayTeamScore": 2,
                "game.league.abbrev": "MLB",
                "selection.label": "Boston -150",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -150,
                "selection.unit": 1.0
            }
        ]

        result = compute_bet_results(sample_bet_data)

        # The result should contain the expected keys.
        expected_keys = {"record", "results", "total_units", "roi"}
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result["record"], {"wins":1, "losses": 0, "draws": 1})
        self.assertAlmostEqual(result["results"], 0.6667, places=4)
        self.assertEqual(result["total_units"], 1.25)
        self.assertAlmostEqual(result["roi"], 0.6667/1.25, places=4)

    def test_compute_bet_results_empty_data(self):
        """Test compute_bet_results with empty bet data."""

        # Expect a ValueError because the data is empty.
        with self.assertRaises(ValueError):
            result = compute_bet_results([])

        # expected_keys = {"record", "results", "total_units", "roi"}
        # self.assertEqual(set(result.keys()), expected_keys)
        # self.assertEqual(result["record"], {"wins": 0, "losses": 0, "draws": 0})

    def test_fetch_expert_picks(self):
        """Test fetch_expert_picks function with expected data."""
        # Load the expected JSON data from file
        test_data_path = os.path.join(os.path.dirname(__file__), 'data', 'Expert_50774572_Next_5_MLB.json')
        
        with open(test_data_path, 'r') as f:
            expected_data = json.load(f)
        
        result = fetch_expert_picks("50774572", leagues="MLB", count=5, after="eyJfaWQiOiI2N2Y0NmExNy0xYzFmLTRlYjAtODI2MC0zYzAxYzVkOGVhNTQtMjk2MzcxMTAtUFJPUC1GSVJTVF81X0lOTklOR1NfSEFORElDQVAiLCJzY2hlZHVsZWREYXRlVGltZSI6IjIwMjUtMDYtMTlUMTc6MDVaIn0=")
        
        # Verify the result matches the expected data
        self.assertEqual(result, expected_data)
        
    def test_fetch_expert_picks_with_multiple_leagues(self):
        """Test fetch_expert_picks function with multiple leagues."""
        result = fetch_expert_picks("51306423", leagues="MLB,NHL", count=5)
        expert_picks = result.get('data', {}).get('expertPicks', {})
        edges = expert_picks.get('edges', [])
        # Check that we got the expected number of picks.
        self.assertEqual(len(edges), 5)

    def test_integration_workflow(self):
        """Test the complete workflow."""

        # Mock call to fetch sportsline expert JSON data.
        json_data = fetch_expert_picks("50774572", leagues="MLB", count=5)

        # Check that the json_data is not an empty dict.
        self.assertNotEqual(json_data, {})

        transformed_data = transform_sportsline_json_data(json_data)

        # Check that the transformed_data is not an empty list.
        self.assertGreater(len(transformed_data), 0)

        # Check that the most recent date (first in the list) in the data is newer than "2025-06-19T00:30:00.000Z"
        # This is the earliest date in the sample data, and it verifies that we are not just getting our test data.
        self.assertGreater(transformed_data[0]["game.scheduledTime"], "2025-06-19T00:30:00.000Z")

        results = compute_bet_results(transformed_data)
        
        # Verify the results structure
        self.assertIn("record", results)
        self.assertIn("results", results)
        self.assertIn("total_units", results)
        self.assertIn("roi", results)


if __name__ == '__main__':
    unittest.main() 
