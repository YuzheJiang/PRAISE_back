from datetime import datetime, timedelta
from dateutil import tz
import pandas as pd
import numpy as np
import os

# Global variables
latExtent = [22.16,22.5277]
lonExtent = [113.816, 114.442]

cellCount = [41, 64]
cellSizeCoord = [0.01, 0.009]

def get_pollutant_data(dir):
    return np.load(dir + "_full.npy")

def UTC2HKT(timestamp):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Hong_Kong')
    fmt = '%Y-%m-%d %H:%M:%S'

    utc = datetime.strptime(str(datetime.utcfromtimestamp(float(timestamp))), '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)

    HK_T = utc.astimezone(to_zone).strftime(fmt)
    return HK_T

def timeInHKT(time_array):
    time_HKT = []
    for x in time_array:
        time_HKT.append(UTC2HKT(x))
    return time_HKT

def data(pollutant_data):
    time = np.load("data/time_full.npy")
    time_data = timeInHKT(time)
    data = dict()
    for i,j in zip(time_data,pollutant_data):
        data[i] = j
    return data

def coordinate_data():
    Features = []
    for i in range(0,cellCount[0]):
        cell_y = i
        for j in range(0, cellCount[1]):
            rect ={"type": 'polygon', "x": None ,"y": None , "coord":[]}
            cell_x =j
            bottomLeft = [latExtent[0] + cellSizeCoord[1]*i, lonExtent[0] + cellSizeCoord[0]*j]
            bottomRight = [bottomLeft[0], bottomLeft[1] + cellSizeCoord[0]]
            topLeft = [bottomLeft[0]+ cellSizeCoord[1], bottomLeft[1]]
            topRight = [bottomRight[0]+ cellSizeCoord[1],bottomRight[1]]
            coords = [bottomLeft, bottomRight, topRight, topLeft]
            rect["x"], rect["y"], rect["coord"] = cell_x, cell_y, coords
            Features.append(rect)
    return Features

def final_data(whole_data, datetime, future_hour):
    d = whole_data[datetime][int(future_hour)]
    coords = coordinate_data()
    for i in coords:
        i['pollutant'] = d[i['y']][i['x']]
    return coords
# def final_data(whole_data, datetime):
#     d = whole_data[datetime]
#     dic = {}
#     for i in range(0,13):
#         dic[i] = coordinate_data()
#         for j in dic[i]:
#             j['pollutant'] = d[i][j['y']][j['x']]
#     return dic

def map_data(Pollutant,Future_hour,Method,Date_time):
    if Method == 'CMAQ':
        root_dir = 'data/CMAQ/' + 'PM10'
        pol_data = get_pollutant_data(root_dir)
    else:
        root_dir ='data/Our_method/'
        pol_data = get_pollutant_data(root_dir)
    whole_data = data(pol_data)
    final_data_ = final_data(whole_data, Date_time, Future_hour)
    df = pd.DataFrame.from_records(final_data_)
    f = df.to_json(orient='records')
    return f

def data_lineChart_1(code):
    if code == "AA":
        data = [[0, 0.6905714485013981], [1, 0.899045966094226], [2, 0.4207424211113504],
                [3, 0.9788165646638738], [4, 0.7148370928364787], [5, 0.385004780669326],
                [6, 0.12485382497514497], [7, 0.8933176518358881], [8, 0.2054264321062833],
                [9, 0.560230657133687], [10, 0.4703659729933596], [11, 0.7480074504850349],
                [12, 0.868300449736342]]
        df = pd.DataFrame(data, columns = ['x', 'y'])
        result = df.to_json(orient='records')
        return result
    if code == "BB":
        data = [[0, 0.7905714485013982], [1, 0.99045966094226], [2, 0.5207424211113504],
                [3, 0.7788165646638738], [4, 0.3148370928364787], [5, 0.185004780669326],
                [6, 0.10485382497514498], [7, 0.4933176518358881], [8, 0.054264321062833],
                [9, 0.360230657133687], [10, 0.5703659729933596], [11, 0.9480074504850349],
                [12, 0.768300449736342]]
        df = pd.DataFrame(data, columns = ['x', 'y'])
        result = df.to_json(orient='records')
        return result

def data_lineChart_2(code):
    if code == "AA":
        data = [[0, 0.7905714485013982], [1, 0.99045966094226], [2, 0.5207424211113504],
                [3, 0.7788165646638738], [4, 0.3148370928364787], [5, 0.185004780669326],
                [6, 0.10485382497514498], [7, 0.4933176518358881], [8, 0.054264321062833],
                [9, 0.360230657133687], [10, 0.5703659729933596], [11, 0.9480074504850349],
                [12, 0.768300449736342]]
        df = pd.DataFrame(data, columns = ['x', 'y'])
        result = df.to_json(orient='records')
        return result
    if code == "BB":
        data = [[0, 0.6905714485013981], [1, 0.899045966094226], [2, 0.4207424211113504],
                [3, 0.9788165646638738], [4, 0.7148370928364787], [5, 0.385004780669326],
                [6, 0.12485382497514497], [7, 0.8933176518358881], [8, 0.2054264321062833],
                [9, 0.560230657133687], [10, 0.4703659729933596], [11, 0.7480074504850349],
                [12, 0.868300449736342]]
        df = pd.DataFrame(data, columns = ['x', 'y'])
        result = df.to_json(orient='records')
        return result
