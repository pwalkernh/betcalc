# betcalc - Sports Betting Calculator API

A Flask-based REST API for sports betting calculations and expert picks data retrieval. This application provides endpoints for calculating payouts, stakes, odds, effective odds after fees, and fetching expert picks from SportsLine.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Building and Running](#building-and-running)
- [Running Tests](#running-tests)
- [API Endpoints](#api-endpoints)
- [OpenAPI Documentation](#openapi-documentation)
- [Development](#development)

## Features

- **Betting Calculations**: Calculate payouts, stakes, and odds for sports bets
- **Effective Odds**: Adjust odds for fees and commissions
- **Expert Picks**: Fetch expert betting picks from SportsLine API
- **Multiple Input Methods**: Support for both POST (JSON) and GET (query parameters)
- **Comprehensive Testing**: Unit tests and API integration tests
- **OpenAPI Specification**: Full API documentation with Swagger

## Quick Start

### With Docker (Recommended)
```bash
# Build the image
docker build -t betcalc .

# Run the application
docker run -p 5000:5000 betcalc

# Or run with development mode and hot reloading
docker run --network=host -v .:/app -e FLASK_ENV=development betcalc flask run
```

### Without Docker
```bash
# Install dependencies
pip install -r ../requirements.txt

# Run the application
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

The API will be available at `http://localhost:5000`

## Building and Running

### Production Mode
```bash
# Using Docker
docker run -p 5000:5000 betcalc

# Without Docker
python app.py
```

### Development Mode
```bash
# Using Docker with hot reloading
docker run --network=host -v .:/app -e FLASK_ENV=development betcalc flask run

# Without Docker
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## Running Tests

### All Tests
```bash
# Using the test runner script (from parent directory)
cd .. && ./run_tests.sh

# Or run individual test files directly
python tests/unit_tests.py
python tests/test_api.py
python tests/test_capper_tracker.py

# or use this shortcut
python -m unittest discover -s tests/ -p "test_*.py" -v
```

### Specific Tests
```bash
# Run a specific test class and method
./run_tests.sh TestBettingCalculator.test_decimal_to_american_odds

# Run a specific test file
python tests/test_api.py TestAPIEndpoints.test_payout_calculation
```

### With Docker
```bash
# Run all tests in container (from parent directory)
cd .. && docker run --rm betcalc ./run_tests.sh

# Run specific test
cd .. && docker run --rm betcalc ./run_tests.sh TestBettingCalculator.test_american_to_decimal_odds
```

## API Endpoints

### Betting Calculations

#### Calculate Payout
- **POST/GET** `/calculate/payout`
- Calculate potential payout and profit from odds and stake
- **Parameters**: `odds` (string), `stake` (number)

#### Calculate Stake  
- **POST/GET** `/calculate/stake`
- Calculate required stake for desired payout at given odds
- **Parameters**: `odds` (string), `payout` (number)

#### Calculate Odds
- **POST/GET** `/calculate/odds`
- Calculate odds needed for desired payout with given stake
- **Parameters**: `stake` (number), `payout` (number)

#### Calculate Effective Odds
- **POST/GET** `/calculate/effective_odds`
- Calculate effective odds after fee adjustment
- **Parameters**: `odds` (string), `fee` (number, optional, default: 0.03)

### Expert Picks

#### Fetch Expert Picks
- **POST/GET** `/fetch/expert-picks`
- Retrieve expert betting picks from SportsLine API
- **Parameters**: `expert` (string, required), `leagues` (string, optional), `after` (string, optional), `count` (integer, optional)

### Example Usage

```bash
# Calculate payout for $100 bet at +150 odds
curl -X POST http://localhost:5000/calculate/payout \
  -H "Content-Type: application/json" \
  -d '{"odds": "+150", "stake": 100}'

# Get expert picks for expert ID 50774572
curl -X GET "http://localhost:5000/fetch/expert-picks?expert=50774572&count=5"

# Calculate effective odds with 3% fee
curl -X GET "http://localhost:5000/calculate/effective_odds?odds=%2B150&fee=0.03"
```

## OpenAPI Documentation

### Viewing the API Specification
- **Raw OpenAPI Spec**: `http://localhost:5000/static/openapi/openapi.yml`
- **API Info Endpoint**: `http://localhost:5000/`

### Using with Swagger UI
1. Copy the OpenAPI spec URL: `http://localhost:5000/static/openapi/openapi.yml`
2. Visit [Swagger Editor](https://editor.swagger.io/) or [Swagger UI](https://petstore.swagger.io/)
3. Paste the spec URL to view interactive documentation

### Local Swagger UI Setup
```bash
# Serve the OpenAPI spec with a simple HTTP server
cd static/openapi
python -m http.server 8080

# Then visit: http://localhost:8080/openapi.yml
```

## Development

### Adding New Endpoints
1. Add the endpoint function to `app.py`
2. Update the OpenAPI specification in `static/openapi/openapi.yml`
3. Add corresponding tests in the `tests/` directory
4. Update this README if needed

### Running in Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

### Environment Variables
- `FLASK_APP`: Set to `app.py` (default)
- `FLASK_ENV`: Set to `development` for debug mode
- `FLASK_DEBUG`: Set to `1` for detailed error messages
