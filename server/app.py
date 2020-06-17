from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask import request

import os,sys
import dataprocessing

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
cors = CORS(app)

# sanity check route
@app.route('/data', methods=['GET'])
def all_data():
    # filter_data = request.get_json()
    filter_col = 'PM25'
    return dataprocessing.get_pollutant_data(filter_col)

if __name__ == '__main__':
    app.run()