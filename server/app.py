from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask import request

import os,sys
import dataprocessing
import json
# instantiate the app
app = Flask(__name__)
cors = CORS(app)

# sanity check route
@app.route("/gridData")
def get_gridData():
    return dataprocessing.coordinate_data()

@app.route("/dummyData", methods=['POST'])
def data():
    filter_data = request.get_json()
    Pollutant = filter_data['pollutants']
    Date_time = filter_data['Date']
    return dataprocessing.get_data(Date_time, Pollutant)

@app.route("/obsData", methods=['POST'])
def observatory_data():
    filter_data = request.get_json()
    Pollutant = filter_data['pollutants']
    Date_time = filter_data['Date']
    return dataprocessing.obs_data(Pollutant, Date_time)

@app.route("/lineChart1", methods=['POST'])
def line1():
    filter_data = request.get_json()
    return dataprocessing.line_chart_1(filter_data, 'Obs_data')

if __name__ == '__main__':
    app.run(debug=True)
