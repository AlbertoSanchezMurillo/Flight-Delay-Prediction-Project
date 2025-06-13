import sys, os, re, json, uuid, datetime
from flask import Flask, render_template, request
from pymongo import MongoClient
from bson import json_util
from kafka import KafkaProducer
import iso8601

# Configuración
import config
import predict_utils
from pyelasticsearch import ElasticSearch

app = Flask(__name__)

# MongoDB
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)

# ElasticSearch
elastic = ElasticSearch(config.ELASTIC_URL)

# Kafka
producer = KafkaProducer(bootstrap_servers=['kafka:9092'], api_version=(0,10))
PREDICTION_TOPIC = 'flight-delay-ml-request'

# Página principal
@app.route("/")
@app.route("/airlines")
@app.route("/airlines/")
def airlines():
    airlines = client.agile_data_science.airplanes_per_carrier.find()
    return render_template('all_airlines.html', airlines=airlines)

# Página de predicción (formulario)
@app.route("/flights/delays/predict_kafka")
def flight_delays_page_kafka():
    form_config = [
        {'field': 'DepDelay', 'label': 'Departure Delay', 'value': 5},
        {'field': 'Carrier', 'value': 'AA'},
        {'field': 'FlightDate', 'label': 'Date', 'value': '2016-12-25'},
        {'field': 'Origin', 'value': 'ATL'},
        {'field': 'Dest', 'label': 'Destination', 'value': 'SFO'}
    ]
    return render_template('flight_delays_predict_kafka.html', form_config=form_config)

# Envío del formulario y publicación en Kafka
@app.route("/flights/delays/predict/classify_realtime", methods=['POST'])
def classify_flight_delays_realtime():
    api_field_type_map = {
        "DepDelay": float,
        "Carrier": str,
        "FlightDate": str,
        "Dest": str,
        "FlightNum": str,
        "Origin": str
    }

    api_form_values = {
        key: request.form.get(key, type=api_field_type_map[key])
        for key in api_field_type_map
    }

    prediction_features = api_form_values.copy()
    prediction_features['Distance'] = predict_utils.get_flight_distance(
        client, api_form_values['Origin'], api_form_values['Dest']
    )

    date_features = predict_utils.get_regression_date_args(api_form_values['FlightDate'])
    prediction_features.update(date_features)
    prediction_features['Timestamp'] = predict_utils.get_current_timestamp()

    unique_id = str(uuid.uuid4())
    prediction_features['UUID'] = unique_id

    message_bytes = json.dumps(prediction_features).encode()
    producer.send(PREDICTION_TOPIC, message_bytes)

    return json_util.dumps({"status": "OK", "id": unique_id})

# Endpoint para polling desde el navegador
@app.route("/flights/delays/predict/classify_realtime/response/<unique_id>")
def classify_flight_delays_realtime_response(unique_id):
    prediction = client.agile_data_science.flight_delay_ml_response.find_one(
        {"UUID": unique_id}
    )

    response = {"status": "WAIT", "id": unique_id}
    if prediction and "Prediction" in prediction:
        response["status"] = "OK"
        response["prediction"] = prediction["Prediction"]

    return json_util.dumps(response)

# Apagar el servidor Flask (para test)
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

# Lanzar servidor
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5010)

