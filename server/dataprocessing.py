from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
import json
from math import sqrt
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

# def final_data(whole_data, datetime, future_hour):
#     d = whole_data[datetime][int(future_hour)]
#     coords = coordinate_data()
#     for i in coords:
#         i['pollutant'] = d[i['y']][i['x']]
#     return coords
def final_data(whole_data, datetime):
    d = whole_data[datetime]
    dic = {}
    for i in range(0,13):
        dic[i] = coordinate_data()
        for j in dic[i]:
            j['pollutant'] = d[i][j['y']][j['x']]
    return dic

def map_data(Method,Pollutant,Date_time):
    if Method == 'CMAQ':
        root_dir = 'data/CMAQ/' + 'PM10'
        pol_data = get_pollutant_data(root_dir)
    else:
        root_dir ='data/Our_method/'
        pol_data = get_pollutant_data(root_dir)
    whole_data = data(pol_data)
    final_data_ = final_data(whole_data, Date_time)
    df = pd.DataFrame.from_records(final_data_)
    f = df.to_json(orient='records')
    return f

def station_coord(key):
    d= {'CB_R': [37,13], 
        'CL_R': [34,13],
        'CW_A': [33,14],
        'EN_A': [40,14],
        'KC_A': [31,22],
        'KT_A': [41,17],
        'MB_A': [55,34],
        'MKaR': [35,18],
        'SP_A': [34,19],
        'ST_A': [37,24],
        'TC_A': [13,14],
        'TK_A': [45,17],
        'TM_A': [16,25],
        'TP_A': [35,32],
        'TW_A': [30,23],
        'YL_A': [21,31]}
    return d[key]

def CMAQ_linedata(code, start_date, end_date, pollutant, Future_hour):
    # variables
    st_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(Future_hour))
    en_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(Future_hour))
    delta = en_date - st_date
    days, seconds = delta.days, delta.seconds
    hours = days * 24 + seconds // 3600
    coords = station_coord(code)
    
    # CMAQ data
    root_dir = 'data/CMAQ/' + pollutant
    pol_data = get_pollutant_data(root_dir)
    whole_data = data(pol_data)
    date_list = [str(st_date + timedelta(hours=i)) for i in range(hours +1)]
    pol_lis = [whole_data[i][int(Future_hour)][coords[0]][coords[1]] for i in date_list]
    df = pd.DataFrame({'time': date_list, 'pollutant': pol_lis})
    df['data'] = 'CMAQ_data'
    return df

def df_concat(dt):
    code = dt['St_code']
    polu = dt['pollutant']
    start_date = dt['st_date']
    end_date = dt['en_date']
    Future_hour = dt['F_hour']
    df_1 = pd.read_csv('data/obs/' + code +'.csv', usecols=['time',polu])
    df_1['time']= (pd.to_datetime(df_1['time']) + pd.Timedelta(hours=8)).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_1 = df_1[(df_1['time'] >= start_date) & (df_1['time'] <= end_date)]
    df_1['data'] = 'Obs_data'
    df_1.rename(columns={polu: 'pollutant'},inplace = True)
    df_2 = CMAQ_linedata(code,start_date,end_date,polu,Future_hour)
    return df_1, df_2

def data_lineChart_1(dt):
    df_1, df_2 = df_concat(dt)
    df = pd.concat([df_1,df_2])
    result = df.to_json(orient='records')
    return result

def IOA(o, s):
    return 1 -(np.sum((o-s)**2))/(np.sum((np.abs(s-np.mean(o))+np.abs(o-np.mean(o)))**2))

def metrics(dt):
    df_1, df_2 = df_concat(dt)
    act = df_1['pollutant'].values
    pred = df_2['pollutant'].values
    rmse = round(sqrt(mean_squared_error(act, pred)),2)
    ioa = round(IOA(act, pred),2)
    return json.dumps([{'RMSE': rmse, 'IOA': ioa}])

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
