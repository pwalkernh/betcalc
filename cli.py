#!/usr/bin/env python3
"""
Command-line interface for the capper tracker functionality.
"""

import argparse
import sys
from datetime import datetime, timedelta
from capper_tracker import fetch_sportsline_expert_webpage, extract_sportsline_json_data, transform_sportsline_json_data, compute_bet_results


def parse_date(date_str):
    """Parse date string in various formats."""
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%m/%d/%Y',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")


def main():
    parser = argparse.ArgumentParser(description='Fetch and analyze SportsLine expert picks')
    parser.add_argument('url', help='SportsLine expert URL to fetch')
    parser.add_argument('--start-date', '-s', 
                       help='Start date (YYYY-MM-DD, MM/DD/YYYY, or ISO format)')
    parser.add_argument('--end-date', '-e',
                       help='End date (YYYY-MM-DD, MM/DD/YYYY, or ISO format)')
    parser.add_argument('--output', '-o',
                       help='Output file for HTML content (optional)')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Extract and display JSON data')
    parser.add_argument('--transform', '-t', action='store_true',
                       help='Transform JSON data to simplified format')
    parser.add_argument('--results', '-r', action='store_true',
                       help='Compute and display betting results')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = parse_date(args.start_date)
        except ValueError as e:
            print(f"Error parsing start date: {e}")
            sys.exit(1)
    
    if args.end_date:
        try:
            end_date = parse_date(args.end_date)
        except ValueError as e:
            print(f"Error parsing end date: {e}")
            sys.exit(1)
    
    try:
        print(f"Fetching data from: {args.url}")
        if start_date:
            print(f"Start date: {start_date}")
        if end_date:
            print(f"End date: {end_date}")
        print()
        
        # Fetch the webpage
        html_content = fetch_sportsline_expert_webpage(args.url, start_date, end_date)
        
        # Save HTML if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML content saved to: {args.output}")
        
        # Extract JSON if requested
        if args.json or args.transform or args.results:
            try:
                json_data = extract_sportsline_json_data(html_content)
                print("✓ Successfully extracted JSON data")
                
                if args.json:
                    import json
                    print("\nJSON Data:")
                    print(json.dumps(json_data, indent=2))
                
                # Transform data if requested
                if args.transform or args.results:
                    transformed_data = transform_sportsline_json_data(json_data)
                    print(f"✓ Transformed {len(transformed_data)} picks")
                    
                    if args.transform:
                        import json
                        print("\nTransformed Data:")
                        print(json.dumps(transformed_data, indent=2))
                    
                    # Compute results if requested
                    if args.results:
                        results = compute_bet_results(transformed_data)
                        print("\nBetting Results:")
                        print(f"Record: {results['record']['wins']}W-{results['record']['losses']}L-{results['record']['draws']}D")
                        print(f"Net Result: {results['results']:.2f} units")
                        print(f"Total Units Wagered: {results['total_units']:.2f}")
                        print(f"ROI: {results['roi']:.2%}")
                
            except Exception as e:
                print(f"Error processing data: {e}")
                sys.exit(1)
        
        print("\n✓ Fetch completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 