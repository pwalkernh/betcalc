# betcalc
Simple betting calculator

# Running the Flask service

```sh
docker run --rm -it --name betcalc-app -p 5000:5000 betcalc:latest
```

# Running all tests

```sh
docker run --rm -it --name betcalc-app -p 5000:5000 ./run_tests.sh
```

# Running a specific unit test

This example runs a single test in the class TestBettingCalculator, with the name "test_decimal_to_american_odds"

```sh
./run_tests.sh TestBettingCalculator.test_decimal_to_american_odds
```
