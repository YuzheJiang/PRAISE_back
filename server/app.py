from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask import request

import os,sys
import dataprocessing

# instantiate the app
app = Flask(__name__)
cors = CORS(app)

# sanity check route
@app.route("/")
def get_allData():
    return "Hello, World!"

@app.route("/data", methods=['POST'])
def load_data():
    filter_data = request.get_json()
    Method = filter_data['Method']
    Pollutant = filter_data['pollutants']
    Date_time = filter_data['Date']
    return dataprocessing.map_data(Method,Pollutant,Date_time)

@app.route("/lineChart1", methods=['POST'])
def lineChart1():
    data = request.get_json()
    return dataprocessing.data_lineChart_1(data)

# @app.route("/lineChart2", methods=['POST'])
# def lineChart2():
#     data = request.get_json()
#     onsite_code = data['Onsite_code']
#     return dataprocessing.data_lineChart_2(onsite_code)


if __name__ == '__main__':
    app.run(debug=True)
