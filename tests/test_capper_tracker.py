
import unittest
import json
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from capper_tracker import (
    fetch_sportsline_expert_webpage,
    extract_sportsline_json_data,
    transform_sportsline_json_data,
    compute_bet_results,
    fields_to_extract
)


class TestCapperTracker(unittest.TestCase):
    """Test cases for capper tracker functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_url = "https://www.sportsline.com/experts/50774572/matt-severance/"

        self.expectedSimplifiedJSON = [
            {
                "resultStatus": "Win",
                "unit": 0.5,
                "game.abbrev": "MLB_20250619_LAA@NYY",
                "game.scheduledTime": "2025-06-19T17:05:00.000Z",
                "game.homeTeamScore": 7,
                "game.awayTeamScore": 3,
                "game.league.abbrev": "MLB",
                "selection.label": "First 5 Innings N.Y. Yankees -0.5 -161",
                "selection.marketType": "PROP",
                "selection.odds": -161,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Loss",
                "unit": 1,
                "game.abbrev": "MLB_20250618_COL@WAS",
                "game.scheduledTime": "2025-06-19T00:30:00.000Z",
                "game.homeTeamScore": 1,
                "game.awayTeamScore": 3,
                "game.league.abbrev": "MLB",
                "selection.label": "Washington -158",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -158,
                "selection.unit": 1,
            },
            {
                "resultStatus": "Loss",
                "unit": 0.25,
                "game.abbrev": "MLB_20250618_BOS@SEA",
                "game.scheduledTime": "2025-06-18T20:10:00.000Z",
                "game.homeTeamScore": 1,
                "game.awayTeamScore": 3,
                "game.league.abbrev": "MLB",
                "selection.label": "Seattle +1.5 -179",
                "selection.marketType": "POINT_SPREAD",
                "selection.odds": -179,
                "selection.unit": 0.25,
            },
            {
                "resultStatus": "Loss",
                "unit": 0.5,
                "game.abbrev": "MLB_20250617_CLE@SF",
                "game.scheduledTime": "2025-06-18T01:45:00.000Z",
                "game.homeTeamScore": 2,
                "game.awayTeamScore": 3,
                "game.league.abbrev": "MLB",
                "selection.label": "San Francisco -160",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -160,
                "selection.unit": 0.5,
            },
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
                "selection.unit": 0.5,
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
                "selection.unit": 1,
            },
            {
                "resultStatus": "Win",
                "unit": 0.5,
                "game.abbrev": "MLB_20250617_COL@WAS",
                "game.scheduledTime": "2025-06-17T22:45:00.000Z",
                "game.homeTeamScore": 6,
                "game.awayTeamScore": 10,
                "game.league.abbrev": "MLB",
                "selection.label": "Luis Garcia Under 1.5 Total Hits -165",
                "selection.marketType": "PROP",
                "selection.odds": -165,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Loss",
                "unit": 0.5,
                "game.abbrev": "MLB_20250616_BOS@SEA",
                "game.scheduledTime": "2025-06-17T01:40:00.000Z",
                "game.homeTeamScore": 0,
                "game.awayTeamScore": 2,
                "game.league.abbrev": "MLB",
                "selection.label": "Seattle -174",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -174,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Win",
                "unit": 0.5,
                "game.abbrev": "NBA_20250616_IND@OKC",
                "game.scheduledTime": "2025-06-17T00:30:00.000Z",
                "game.homeTeamScore": 120,
                "game.awayTeamScore": 109,
                "game.league.abbrev": "NBA",
                "selection.label": "Shai Gilgeous-Alexander Under 35.5 Total Points -125",
                "selection.marketType": "PROP",
                "selection.odds": -125,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Loss",
                "unit": 0.5,
                "game.abbrev": "MLB_20250616_LAA@NYY",
                "game.scheduledTime": "2025-06-16T23:05:00.000Z",
                "game.homeTeamScore": 0,
                "game.awayTeamScore": 1,
                "game.league.abbrev": "MLB",
                "selection.label": "N.Y. Yankees -188",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -188,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Win",
                "unit": 0.5,
                "game.abbrev": "MLB_20250615_CHW@TEX",
                "game.scheduledTime": "2025-06-15T18:35:00.000Z",
                "game.homeTeamScore": 2,
                "game.awayTeamScore": 1,
                "game.league.abbrev": "MLB",
                "selection.label": "Texas -164",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -164,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Loss",
                "unit": 0.5,
                "game.abbrev": "MLB_20250615_CIN@DET",
                "game.scheduledTime": "2025-06-15T16:05:00.000Z",
                "game.homeTeamScore": 4,
                "game.awayTeamScore": 8,
                "game.league.abbrev": "MLB",
                "selection.label": "Detroit -182",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -182,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Win",
                "unit": 0.5,
                "game.abbrev": "MLB_20250614_SF@LAD",
                "game.scheduledTime": "2025-06-15T02:10:00.000Z",
                "game.homeTeamScore": 11,
                "game.awayTeamScore": 5,
                "game.league.abbrev": "MLB",
                "selection.label": "L.A. Dodgers -172",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -172,
                "selection.unit": 0.5,
            },
            {
                "resultStatus": "Loss",
                "unit": 1,
                "game.abbrev": "NHL_20250614_FLA@EDM",
                "game.scheduledTime": "2025-06-15T00:00:00.000Z",
                "game.homeTeamScore": 2,
                "game.awayTeamScore": 5,
                "game.league.abbrev": "NHL",
                "selection.label": "Edmonton -116",
                "selection.marketType": "MONEY_LINE",
                "selection.odds": -116,
                "selection.unit": 1,
            },
        ]

    def test_fetch_sportsline_expert_webpage_basic(self):
        """Test basic functionality of fetch_sportsline_expert_webpage."""

        html = fetch_sportsline_expert_webpage(self.sample_url)

        # Check that the html is not an empty string.
        self.assertNotEqual(html, "")

        # Check that valid html is returned.
        self.assertIn("<html>", html)
        self.assertIn("</html>", html)
        self.assertIn("<body>", html)
        self.assertIn("</body>", html)

    def test_extract_sportsline_json_data(self):
        """Test basic functionality of extract_sportsline_json_data."""
        with open('tests/data/Matt Severance - Vegas Expert Picks - Severance Pays - SportsLine.com.html', 'r', encoding='utf-8') as f:
            html = f.read()

        result = extract_sportsline_json_data(html)

        # Load the expected JSON data from the sample file
        with open('tests/data/Matt_Severance_Sample.json', 'r', encoding='utf-8') as f:
            expected_json = json.load(f)

        # Verify the extracted JSON matches the expected structure
        self.assertEqual(result, expected_json)

    def test_extract_sportsline_json_data_no_json(self):
        """Test extract_sportsline_json_data with HTML containing no JSON."""
        html = "<html><body>No JSON here</body></html>"

        with self.assertRaises(ValueError):
            result = extract_sportsline_json_data(html)

    def test_transform_sportsline_json_data_with_sample_data(self):
        """Test basic functionality of transform_sportsline_json_data."""
        with open('tests/data/Matt_Severance_Sample.json', 'r', encoding='utf-8') as f:
            sample_json = json.load(f)

        result = transform_sportsline_json_data(sample_json)

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

    def test_integration_workflow(self):
        """Test the complete workflow from HTML to results.
        Verify that the data covers the time period requested."""

        html = fetch_sportsline_expert_webpage(self.sample_url)

        # Check that the html is not an empty string.
        self.assertNotEqual(html, "")

        json_data = extract_sportsline_json_data(html)

        # Check that the json_data is not an empty dict.
        self.assertNotEqual(json_data, {})

        transformed_data = transform_sportsline_json_data(json_data)

        # Check that the transformed_data is not an empty list.
        self.assertGreater(len(transformed_data), 0)

        # Check that the most recent date (first in the list) in the data is newer than "2025-06-19T00:30:00.000Z"
        # This is the earliest date in the sample data.
        self.assertGreater(transformed_data[0]["game.scheduledTime"], "2025-06-19T00:30:00.000Z")

        results = compute_bet_results(transformed_data)


if __name__ == '__main__':
    unittest.main() 
