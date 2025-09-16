from flask import Flask, request, jsonify
from flask_cors import CORS
from models import FlightInfo
from data_fetcher import FlightDataAggregator
from fs_agent import FlightServiceAgent


app = Flask(__name__)
CORS(app)

# Initialize the Flight Service Agent
try:
    flight_agent = FlightServiceAgent()
    print("Flight Service Agent initialized successfully")
except Exception as e:
    print(f"Warning: Failed to initialize Flight Service Agent: {e}")
    flight_agent = None

@app.route('/api/flight', methods=['POST'])
def flight_info():
    data = request.json
    flight_info_obj = FlightInfo(data)
    
    # Fetch online resources
    data_aggregator = FlightDataAggregator()
    online_data = data_aggregator.fetch_flight_data(
        departure_airport=flight_info_obj.pilot_data.departure_airport,
        destination_airport=flight_info_obj.pilot_data.destination_airport,
        alternate_airports=flight_info_obj.pilot_data.alternate_airports
    )
    
    # Populate online resources in flight info
    flight_info_obj.online_resources.weather = online_data['weather']
    flight_info_obj.online_resources.airport_info = online_data['airports']
    flight_info_obj.online_resources.notams = online_data['notams']
    flight_info_obj.online_resources.navaid_info = online_data['navaid_info']
    flight_info_obj.online_resources.airspace_info = online_data['airspace_info']
    
    # Generate AI analysis using FlightServiceAgent
    if flight_agent:
        try:
            print("Generating AI analysis...")
            ai_analysis = flight_agent.sync_analyze_flight_data(flight_info_obj.to_dict())
            
            # Parse the AI analysis and populate the ai_analysis object
            flight_info_obj.ai_analysis.briefing = ai_analysis
            
            print("AI analysis completed successfully")
        except Exception as e:
            print(f"Error generating AI analysis: {e}")
            flight_info_obj.ai_analysis.briefing = f"AI analysis failed: {str(e)}"
    else:
        flight_info_obj.ai_analysis.briefing = "AI analysis unavailable - agent not initialized"
    
    return jsonify({"status": "success", "flight_info": flight_info_obj.to_dict()})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
