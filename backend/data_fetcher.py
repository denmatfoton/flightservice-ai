import requests
import json
from typing import Dict, List, Optional


class WeatherService:
    """Service for fetching weather data from AviationWeather.gov"""
    
    BASE_URL = "https://aviationweather.gov/api/data"
    
    @staticmethod
    def get_metar(airport_codes: str, hours: int = 2) -> Optional[List[Dict]]:
        """
        Fetch METAR data for given airport codes
        
        Args:
            airport_codes: Comma-separated airport codes (e.g., 'KRNT,KORD')
            hours: Hours back to search (default: 2)
            
        Returns:
            List of METAR data dictionaries or None if error
        """
        try:
            url = f"{WeatherService.BASE_URL}/metar"
            params = {
                'ids': airport_codes,
                'format': 'json',
                'hours': hours
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching METAR data: {e}")
            return None
    
    @staticmethod
    def get_taf(airport_codes: str) -> Optional[List[Dict]]:
        """
        Fetch TAF data for given airport codes
        
        Args:
            airport_codes: Comma-separated airport codes (e.g., 'KRNT,KORD')
            
        Returns:
            List of TAF data dictionaries or None if error
        """
        try:
            url = f"{WeatherService.BASE_URL}/taf"
            params = {
                'ids': airport_codes,
                'format': 'json'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching TAF data: {e}")
            return None
    
    @staticmethod
    def get_pireps(airport_code: str, distance: int = 50) -> Optional[List[Dict]]:
        """
        Fetch PIREP data around given airport
        
        Args:
            airport_code: Single airport code (e.g., 'KRNT')
            distance: Radial distance to search in statute miles
            
        Returns:
            List of PIREP data dictionaries or None if error
        """
        try:
            url = f"{WeatherService.BASE_URL}/pirep"
            params = {
                'id': airport_code,
                'distance': distance,
                'format': 'json',
                'age': 6  # 6 hours back
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching PIREP data: {e}")
            return None


class AirportService:
    """Service for fetching airport and navigational data"""
    
    BASE_URL = "https://aviationweather.gov/api/data"
    
    @staticmethod
    def get_airport_info(airport_codes: str) -> Optional[List[Dict]]:
        """
        Fetch airport information
        
        Args:
            airport_codes: Comma-separated airport codes (e.g., 'KRNT,KORD')
            
        Returns:
            List of airport info dictionaries or None if error
        """
        try:
            url = f"{AirportService.BASE_URL}/airport"
            params = {
                'ids': airport_codes,
                'format': 'json'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching airport info: {e}")
            return None
    
    @staticmethod
    def get_navaid_info(navaid_ids: str) -> Optional[List[Dict]]:
        """
        Fetch navigational aid information
        
        Args:
            navaid_ids: Comma-separated navaid IDs
            
        Returns:
            List of navaid info dictionaries or None if error
        """
        try:
            url = f"{AirportService.BASE_URL}/navaid"
            params = {
                'ids': navaid_ids,
                'format': 'json'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching navaid info: {e}")
            return None


class FlightDataAggregator:
    """Main service for aggregating all flight-related data"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.airport_service = AirportService()
    
    def fetch_flight_data(self, departure_airport: str, destination_airport: str, 
                         alternate_airports: str = "") -> Dict:
        """
        Fetch all relevant data for a flight
        
        Args:
            departure_airport: Departure airport code
            destination_airport: Destination airport code
            alternate_airports: Comma-separated alternate airport codes
            
        Returns:
            Dictionary containing all fetched data
        """
        # Combine all airports for weather data
        all_airports = [departure_airport, destination_airport]
        if alternate_airports:
            all_airports.extend(alternate_airports.split(','))
        
        airport_codes = ','.join(filter(None, all_airports))
        
        # Fetch weather data
        metar_data = self.weather_service.get_metar(airport_codes)
        taf_data = self.weather_service.get_taf(airport_codes)
        
        # Fetch PIREPs for departure and destination
        departure_pireps = self.weather_service.get_pireps(departure_airport)
        destination_pireps = self.weather_service.get_pireps(destination_airport)
        
        # Fetch airport information
        airport_info = self.airport_service.get_airport_info(airport_codes)
        
        return {
            'weather': {
                'metar': metar_data or [],
                'taf': taf_data or [],
                'pireps': {
                    'departure': departure_pireps or [],
                    'destination': destination_pireps or []
                }
            },
            'airports': airport_info or [],
            'notams': [],  # TODO: Implement NOTAM fetching
            'navaid_info': {},  # TODO: Implement based on route
            'airspace_info': {}  # TODO: Implement airspace data
        }