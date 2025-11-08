# Personalized Carbon Footprint Tracker

This project is a Python-based tool for calculating and tracking your personal carbon footprint from travel. It integrates Google Maps APIs for geocoding and distance calculation, and the Climatiq API for CO2 emissions estimates. Data is stored in a CSV file for ongoing tracking, setting the stage for analysis with Pandas/NumPy and visualization with Matplotlib. The project supports iterative development with Git and can be extended with DVC for data versioning.

## Features
- **User Input:** Prompt for start and end cities to calculate travel distance.
- **Geocoding:** Converts city names to latitude/longitude using Google Maps Geocoding API, with caching for efficiency.
- **Distance Calculation:** Computes driving distance using Google Routes API.
- **CO2 Estimation:** Estimates emissions for the trip using Climatiq API (currently hardcoded for cars in the US region).
- **Data Storage:** Appends trip details (cities, distance in km, CO2 in kg, date) to a CSV file (`data/history.csv`) using Pandas.
- **Error Handling:** Includes logging for network errors and input validation for non-empty cities.
- **Parallel Processing:** Uses concurrent futures for faster geocoding of multiple locations.
- **Extensibility:** Ready for adding transport modes (e.g., bike, plane), analysis (e.g., trends with NumPy), and visualization (e.g., reduction plots with Matplotlib).

## Requirements
- Python 3.12+
- Libraries: `requests`, `pandas`, `numpy`, `matplotlib`, `python-dotenv`, `shelve`
- API Keys:
  - Google Maps API key (for Geocoding and Routes).
  - Climatiq API key (for emissions estimates).

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/carbon-tracker.git
   cd carbon-tracker
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install requests pandas numpy matplotlib python-dotenv
   ```
4. Set up API keys in a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   CLIMATIQ_API_KEY=your_climatiq_api_key_here
   ```
5. (Optional) Create `cache/` and `data/` directories if not auto-created.

## Usage
Run the script from the command line:
```
python carbon-tracker.py
```
- You'll be prompted for start and end cities.
- The script calculates distance and CO2 emissions, prints results, and appends to `data/history.csv`.

Example output:
```
Enter name of a city where you started your travels: New York
Enter name of a city where you ended your travels: Los Angeles
New York - Latitude: 40.7127753, Longitude: -74.0059728
Los Angeles - Latitude: 34.0522342, Longitude: -118.2436849
Distance from New York to Los Angeles: 3936.7 km  # Note: Actual value may vary
Estimated CO2 emissions for the trip: 1365 kg
Trip data saved to history.csv
```

### CSV Structure
The `history.csv` file will have columns: `start_city`, `end_city`, `distance_km`, `co2_kg`, `date`.

Example row:
```
start_city,end_city,distance_km,co2_kg,date
New York,Los Angeles,3936.7,1365.23,2025-11-08 12:00:00
```

## Configuration and Customization
- **Caching:** Geocoding results are cached in `cache/geocode.db` to reduce API calls.
- **Logging:** Errors (e.g., network issues) are logged to console.
- **Extensions:**
  - Add transport mode selection: Modify `find_distance` and `find_co2` to accept parameters for different modes (e.g., "BICYCLE" for Google, corresponding activity_id for Climatiq).
  - Analysis: Load CSV with Pandas and use NumPy for stats (e.g., total CO2 over time).
  - Visualization: Add Matplotlib plots for trends (e.g., line chart of CO2 by date).
  - DVC Integration: After saving CSV, run `dvc add data/history.csv` and commit with Git.

## Potential Improvements
- Support multiple transport modes (car, bike, plane) with user prompts.
- Handle API rate limits and errors more gracefully.
- Implement DVC pipelines for data tracking.
- Add unit tests for functions.

## License
MIT License. See [LICENSE](LICENSE) for details.

## Contributing
Fork the repo, create a feature branch, and submit a pull request. For issues, open a GitHub issue.