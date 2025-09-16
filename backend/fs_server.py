from flask import Flask, request, jsonify
from flask_cors import CORS
from models import FlightInfo
from data_fetcher import FlightDataAggregator


app = Flask(__name__)
CORS(app)

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
    
    return jsonify({"status": "success", "flight_info": flight_info_obj.to_dict()})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
