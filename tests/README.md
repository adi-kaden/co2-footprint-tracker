# Carbon Tracker Unit Tests

This directory contains unit tests for the carbon footprint tracker application.

## Test Coverage

### 1. `test_get_lat_lon_valid_address`
Tests that `get_lat_lon()` returns correct coordinates for a valid address.
- Mocks the Google Geocoding API response
- Verifies the function returns the expected latitude and longitude
- Checks that the API is called with correct parameters

### 2. `test_get_lat_lon_invalid_address`
Tests that `get_lat_lon()` raises a `ValueError` for an invalid address.
- Mocks an API response with `ZERO_RESULTS` status
- Verifies that a `ValueError` is raised
- Checks that the error message contains relevant information

### 3. `test_find_distance_valid_coordinates`
Tests that `find_distance()` returns the correct distance between two valid coordinates.
- Mocks the Google Routes API response
- Verifies the function returns the expected distance in meters
- Checks that the API is called with correct coordinate parameters

### 4. `test_find_co2_valid_distance`
Tests that `find_co2()` returns the correct CO2 emissions for a given distance.
- Mocks the Climatiq API response
- Verifies the function correctly converts CO2 from grams to kilograms
- Checks that the API is called with correct distance parameters

### 5. `test_history_csv_created_and_updated`
Tests that `history.csv` is created and updated correctly with new trip data.
- Creates a temporary directory for testing
- Simulates adding multiple trips to the CSV
- Verifies that the CSV is created with correct data
- Checks that subsequent trips are appended correctly

### 6. `test_history_csv_columns_correct`
Tests that `history.csv` has the correct column structure.
- Verifies the CSV contains the expected columns: `start_city`, `end_city`, `distance_km`, `co2_kg`, `date`
- Checks that data is saved in the correct format

## Running the Tests

To run all tests:
```bash
pytest tests/test_carbon_tracker.py -v
```

To run a specific test class:
```bash
pytest tests/test_carbon_tracker.py::TestGetLatLon -v
```

To run a specific test:
```bash
pytest tests/test_carbon_tracker.py::TestGetLatLon::test_get_lat_lon_valid_address -v
```

## Dependencies

The tests require:
- `pytest`
- `pandas`
- `unittest.mock` (built-in)

## Notes

- All API calls are mocked to avoid making actual requests during testing
- The history CSV tests use temporary directories that are cleaned up after each test
- The source file was renamed from `carbon-tracker.py` to `carbon_tracker.py` to make it importable as a Python module
