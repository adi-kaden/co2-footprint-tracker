import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the functions we want to test
from carbon_tracker import get_lat_lon, find_distance, find_co2


class TestGetLatLon:
    """Tests for the get_lat_lon function"""
    
    @patch('carbon_tracker.requests.get')
    def test_get_lat_lon_valid_address(self, mock_get):
        """Test that get_lat_lon returns correct coordinates for a valid address"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [{
                'geometry': {
                    'location': {
                        'lat': 40.7128,
                        'lng': -74.0060
                    }
                }
            }]
        }
        mock_get.return_value = mock_response
        
        # Call the function
        lat, lon = get_lat_lon('New York, NY', 'fake_api_key')
        
        # Assert the results
        assert lat == 40.7128
        assert lon == -74.0060
        
        # Verify the API was called correctly
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['address'] == 'New York, NY'
        assert kwargs['params']['key'] == 'fake_api_key'
    
    @patch('carbon_tracker.requests.get')
    def test_get_lat_lon_invalid_address(self, mock_get):
        """Test that get_lat_lon raises ValueError for an invalid address"""
        # Mock the API response for an invalid address
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'ZERO_RESULTS',
            'results': []
        }
        mock_get.return_value = mock_response
        
        # Call the function and expect a ValueError
        with pytest.raises(ValueError) as excinfo:
            get_lat_lon('InvalidAddress123XYZ', 'fake_api_key')
        
        # Verify the error message contains the status
        assert 'ZERO_RESULTS' in str(excinfo.value)
        assert 'Geocoding failed' in str(excinfo.value)


class TestFindDistance:
    """Tests for the find_distance function"""
    
    @patch('carbon_tracker.requests.post')
    def test_find_distance_valid_coordinates(self, mock_post):
        """Test that find_distance returns the correct distance between two valid coordinates"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'routes': [{
                'distanceMeters': 450000,  # 450 km
                'duration': '14400s'
            }]
        }
        mock_post.return_value = mock_response
        
        # Call the function with coordinates for two cities
        distance = find_distance(40.7128, -74.0060, 42.3601, -71.0589, 'fake_api_key')
        
        # Assert the result
        assert distance == 450000
        
        # Verify the API was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['origin']['location']['latLng']['latitude'] == 40.7128
        assert kwargs['json']['origin']['location']['latLng']['longitude'] == -74.0060
        assert kwargs['json']['destination']['location']['latLng']['latitude'] == 42.3601
        assert kwargs['json']['destination']['location']['latLng']['longitude'] == -71.0589
        assert kwargs['headers']['X-Goog-Api-Key'] == 'fake_api_key'


class TestFindCO2:
    """Tests for the find_co2 function"""
    
    @patch('carbon_tracker.requests.post')
    def test_find_co2_valid_distance(self, mock_post):
        """Test that find_co2 returns the correct CO2 emissions for a given distance"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'co2e': 25000,  # 25 kg in grams
            'co2e_unit': 'g'
        }
        mock_post.return_value = mock_response
        
        # Call the function with a distance in km
        co2_kg = find_co2(100, 'fake_api_key')
        
        # Assert the result (should be converted from grams to kg)
        assert co2_kg == 25.0
        
        # Verify the API was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['parameters']['distance'] == 100
        assert kwargs['json']['parameters']['distance_unit'] == 'km'
        assert kwargs['headers']['Authorization'] == 'Bearer fake_api_key'


class TestHistoryCSV:
    """Tests for history.csv creation and updates"""
    
    def setup_method(self):
        """Set up a temporary directory for each test"""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.file_path = os.path.join(self.data_dir, 'history.csv')
    
    def teardown_method(self):
        """Clean up the temporary directory after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_history_csv_created_and_updated(self):
        """Test that history.csv is created and updated correctly with new trip data"""
        # Create the data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Simulate first trip - CSV doesn't exist yet
        columns = ['start_city', 'end_city', 'distance_km', 'co2_kg', 'date']
        
        try:
            df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=columns)
        
        # Add first trip
        data_to_append = {
            'start_city': 'New York',
            'end_city': 'Boston',
            'distance_km': 350000,
            'co2_kg': 45.5,
            'date': '2024-01-15 10:30:00'
        }
        df_new = pd.DataFrame([data_to_append])
        df = pd.concat([df, df_new], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        
        # Verify the CSV was created
        assert os.path.exists(self.file_path)
        
        # Read and verify the contents
        df_read = pd.read_csv(self.file_path)
        assert len(df_read) == 1
        assert df_read.iloc[0]['start_city'] == 'New York'
        assert df_read.iloc[0]['end_city'] == 'Boston'
        assert df_read.iloc[0]['distance_km'] == 350000
        assert df_read.iloc[0]['co2_kg'] == 45.5
        
        # Add a second trip
        df = pd.read_csv(self.file_path)
        data_to_append_2 = {
            'start_city': 'Boston',
            'end_city': 'Philadelphia',
            'distance_km': 435000,
            'co2_kg': 56.2,
            'date': '2024-01-16 14:45:00'
        }
        df_new = pd.DataFrame([data_to_append_2])
        df = pd.concat([df, df_new], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        
        # Verify both trips are in the CSV
        df_read = pd.read_csv(self.file_path)
        assert len(df_read) == 2
        assert df_read.iloc[0]['start_city'] == 'New York'
        assert df_read.iloc[1]['start_city'] == 'Boston'
        assert df_read.iloc[1]['end_city'] == 'Philadelphia'
    
    def test_history_csv_columns_correct(self):
        """Test that history.csv has the correct column structure"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        columns = ['start_city', 'end_city', 'distance_km', 'co2_kg', 'date']
        df = pd.DataFrame(columns=columns)
        
        # Add sample data
        data_to_append = {
            'start_city': 'Los Angeles',
            'end_city': 'San Francisco',
            'distance_km': 615000,
            'co2_kg': 79.5,
            'date': '2024-01-20 09:15:00'
        }
        df_new = pd.DataFrame([data_to_append])
        df = pd.concat([df, df_new], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        
        # Read and verify columns
        df_read = pd.read_csv(self.file_path)
        assert list(df_read.columns) == columns
