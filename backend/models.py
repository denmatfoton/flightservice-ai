class PilotProvidedData:
    def __init__(self, data):
        self.pilot_name = data.get('pilotName', '')
        self.pilot_qualifications = data.get('pilotQualifications', '')
        self.flight_rules = data.get('flightRules', '')
        self.aircraft_type = data.get('aircraftType', '')
        self.aircraft_equipment = data.get('aircraftEquipment', '')
        self.true_airspeed = data.get('trueAirspeed', '')
        self.departure_airport = data.get('departureAirport', '')
        self.destination_airport = data.get('destinationAirport', '')
        self.takeoff_time = data.get('takeoffTime', '')
        self.estimated_enroute = data.get('estimatedEnroute', '')
        self.alternate_airports = data.get('alternateAirports', '')

    def to_dict(self):
        return {
            "pilot_name": self.pilot_name,
            "pilot_qualifications": self.pilot_qualifications,
            "flight_rules": self.flight_rules,
            "aircraft_type": self.aircraft_type,
            "aircraft_equipment": self.aircraft_equipment,
            "true_airspeed": self.true_airspeed,
            "departure_airport": self.departure_airport,
            "destination_airport": self.destination_airport,
            "takeoff_time": self.takeoff_time,
            "estimated_enroute": self.estimated_enroute,
            "alternate_airports": self.alternate_airports,
        }


class OnlineResources:
    def __init__(self):
        self.weather = {}
        self.notams = []
        self.pireps = []
        self.airport_info = {}
        self.navaid_info = {}
        self.airspace_info = {}

    def to_dict(self):
        return {
            "weather": self.weather,
            "notams": self.notams,
            "pireps": self.pireps,
            "airport_info": self.airport_info,
            "navaid_info": self.navaid_info,
            "airspace_info": self.airspace_info,
        }


class AIAnalysis:
    def __init__(self):
        self.briefing = ""
        self.recommendations = []
        self.weather_analysis = ""
        self.route_analysis = ""
        self.risk_assessment = ""
        self.alternate_recommendations = []

    def to_dict(self):
        return {
            "briefing": self.briefing,
            "recommendations": self.recommendations,
            "weather_analysis": self.weather_analysis,
            "route_analysis": self.route_analysis,
            "risk_assessment": self.risk_assessment,
            "alternate_recommendations": self.alternate_recommendations,
        }


class FlightInfo:
    def __init__(self, data):
        self.pilot_data = PilotProvidedData(data)
        self.online_resources = OnlineResources()
        self.ai_analysis = AIAnalysis()

    def to_dict(self):
        return {
            "pilot_data": self.pilot_data.to_dict(),
            "online_resources": self.online_resources.to_dict(),
            "ai_analysis": self.ai_analysis.to_dict(),
        }