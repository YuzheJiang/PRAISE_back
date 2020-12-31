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
<<<<<<< HEAD
    Pollutant = filter_data['pollutants'].split()[0]
=======
    Pollutant = filter_data['pollutants']
>>>>>>> 584871148ef753b8fe2ae7ac88a8c0b0d777fd92
    Date_time = filter_data['Date']
    return dataprocessing.get_data(Date_time, Pollutant)

@app.route("/obsData", methods=['POST'])
def observatory_data():
    filter_data = request.get_json()
<<<<<<< HEAD
    Pollutant = filter_data['pollutants'].split()[0]
=======
    Pollutant = filter_data['pollutants']
>>>>>>> 584871148ef753b8fe2ae7ac88a8c0b0d777fd92
    Date_time = filter_data['Date']
    return dataprocessing.obs_data(Pollutant, Date_time)

@app.route("/lineChart1", methods=['POST'])
def line1():
    filter_data = request.get_json()
    return dataprocessing.line_chart_1(filter_data, 'Obs_data')
<<<<<<< HEAD

@app.route("/lineChart2", methods=['POST'])
def line2():
    filter_data = request.get_json()
    return dataprocessing.line_chart_2(filter_data, 'onsite_data')
=======
>>>>>>> 584871148ef753b8fe2ae7ac88a8c0b0d777fd92

if __name__ == '__main__':
    app.run(debug=True)
