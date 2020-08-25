from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
from glob import glob
from math import sqrt
from dateutil import tz
import pandas as pd
import numpy as np
import json
import os

# Global variables
latExtent = [22.16,22.5277]
lonExtent = [113.816, 114.442]

cellCount = [41, 64]
cellSizeCoord = [0.01, 0.009]

# def check_month(d, directory):
#     month = datetime.strptime(d, '%Y-%m-%d %H:%M:%S').month
#     for i in os.listdir(directory):
#         if i.endswith('.npy') and datetime.strptime(i[:-4], '%Y-%m-%d %H:%M:%S').month == month:
#             path = os.path.join(directory,i)
#     return path

def obs_data(Pollutant, Date_time):
    date_list = [(datetime.strptime(Date_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=x)).strftime('%Y-%m-%d %H:%M:%S') for x in range(0,13)]
    df = pd.read_csv('data/cache/obs/Obs_data.csv', usecols=['time',Pollutant, 'x', 'y']).rename(columns={Pollutant: "Pollutant"})
    df = df[df['time'].isin(date_list)]
    grouped = df.groupby(['time'])
    d = {}
    for index, group_item in enumerate(grouped):
        lis = []
        for i in group_item[1].iterrows():
            dic = {}
            dic['Pollutant'], dic['x'], dic['y'] = i[1]['Pollutant'], i[1]['x'], i[1]['y']
            lis.append(dic)
        d[index] = lis
    return json.dumps(d)

# Getting the coordinate range for plotting the map
def coordinate_data():
    Features = []
    coordinate_list = [[37,13], [34,13], [33,14], [40,14], [31,22], [41,17], [55,34], [35,18], 
                   [34,19], [37,24], [13,14], [45,17], [16,25], [35,32], [30,23], [21,31]]
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
            if [cell_x, cell_y] in coordinate_list:
                rect["x"], rect["y"], rect["coord"], rect['data'] = cell_x, cell_y, coords, 'Observatory_data'
            else:
                rect["x"], rect["y"], rect["coord"], rect['data'] = cell_x, cell_y, coords, 'Grid_data'
            Features.append(rect)
    return json.dumps(Features)

def get_data(date, Pollutant):
    month = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S').month]
    dic = {}
    for i in ['CMAQ', 'Our_method'] :
        directory = os.path.join('data','cache',i,Pollutant)
        data, filename = month_data(month, directory)
        diff = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')-datetime.strptime(filename[:-4], '%Y-%m-%d %H:%M:%S')
        hours = diff.days * 24 + diff.seconds // 3600
        dic[i] = data[hours].tolist()
    return json.dumps(dic)      
       
def time_poldata(pol_data, start_date):
    time_data = np.load('data/cache/time_data.npy')
    df = pd.DataFrame(time_data, columns = ['time'])
    df = df[df.time >= str(start_date)]
    data = {}
    for i,j in zip(df.iterrows(),pol_data):
        data[i[1]['time']] = j
    return data

def month_data(month_list, direc):
    final_data = []
    for file in os.listdir(direc):
        if file.endswith('.npy') and datetime.strptime(file[:-4], '%Y-%m-%d %H:%M:%S').month in month_list:
            data = np.load(os.path.join(direc,file))
            final_data.append(data)
    return np.concatenate(final_data), file

# Getting the metrics value 
def metrics(df_1, df_2):
    act = df_1['Pollutant'].values
    pred = df_2['Pollutant'].values
    rmse = round(sqrt(mean_squared_error(act, pred)),2)
    ioa = round(1 -(np.sum((act-pred)**2))/(np.sum((np.abs(pred-np.mean(act))+np.abs(act-np.mean(act)))**2)), 2)
    return rmse, ioa

# Station code with coordinates
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

def obs_onsite_data(path, code, Pollutant, date_list):
    df = pd.read_csv(path, usecols=['time', 'station_code', Pollutant]).rename(columns={Pollutant: "Pollutant"})
    df = df[((df["time"].isin(date_list)) & (df["station_code"] == code))].drop(['station_code'], axis=1)
    df['data'] = 'station_data'
    return df

def arguments(dt):
    start_date = dt['st_date']
    end_date = dt['en_date']
    Future_hour = dt['F_hour']

    st_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(Future_hour))
    en_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(Future_hour))
    delta = en_date - st_date
    hours = delta.days * 24 + delta.seconds // 3600
    date_list = [str(datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=i)) for i in range(hours +1)]
    date_list_1 = [str(st_date + timedelta(hours=i)) for i in range(hours +1)]
    return st_date, en_date, date_list, date_list_1, Future_hour

def line_chart_1(dt, station_type):
    Pollutant = dt['pollutant']
    code = dt['St_code']

    data = []
    metric = {}
    st_date, en_date, date_list, date_list_1, Future_hour = arguments(dt)
    station_df = obs_onsite_data('data/cache/obs/'+ station_type +'.csv', code, Pollutant, date_list)
    data.append(station_df)
    for i in ['CMAQ', 'Our_method']:
        directory = os.path.join('data','cache',i,Pollutant)
        month = [st_date.month, en_date.month]
        coords = station_coord(code)
        final_data, filename = month_data(month,directory)
        whole_data = time_poldata(final_data, st_date)
        pol_lis = [whole_data[i][int(Future_hour)][coords[1]][coords[0]] for i in date_list_1]
        method_data = pd.DataFrame({'time': date_list, 'Pollutant': pol_lis, 'data': i+'_data'})
        data.append(method_data)
        RMSE, IOA = metrics(method_data, station_df)
        metric['RMSE_'+i], metric['IOA_'+i] =  RMSE, IOA
    df = pd.concat(data)
    result = df.to_dict('records')
    return json.dumps([{'RMSE': metric['RMSE_CMAQ'] , 'IOA': metric['IOA_CMAQ'], 'RMSE_our': metric['RMSE_Our_method'] , 'IOA_our': metric['IOA_Our_method'], 'line_data': result}])