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

# Code for concentration map

# Loading the pollutant data
def get_pollutant_data(dir):
    return np.load(dir + "_full.npy")

# Formula for the timestamp conversion(UTC to HKT)
def UTC2HKT(timestamp):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Hong_Kong')
    fmt = '%Y-%m-%d %H:%M:%S'

    utc = datetime.strptime(str(datetime.utcfromtimestamp(float(timestamp))), '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)

    HK_T = utc.astimezone(to_zone).strftime(fmt)
    return HK_T

# Code for actual conversion(UTC to HKT)
def timeInHKT(time_array):
    time_HKT = []
    for x in time_array:
        time_HKT.append(UTC2HKT(x))
    return time_HKT

# Getting the time data
def data(pollutant_data):
    time = np.load("data/time_full.npy")
    time_data = timeInHKT(time)
    data = dict()
    for i,j in zip(time_data,pollutant_data):
        data[i] = j
    return data

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
    return Features

# Getting Observation data for map
def Obs_mapdata(Pollutant, Date_time):
    files = sorted(glob('data/obs/*.csv'))
    date_list = [(datetime.strptime(Date_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=x)).strftime('%Y-%m-%d %H:%M:%S') for x in range(0,13)]
    df = pd.concat((pd.read_csv(file, index_col=0)for file in files), ignore_index = True)
    df.sort_values(by=['time', 'station_code'])
    df['time'] =  pd.to_datetime(df['time'])
    df = df[df['time'].isin(date_list)]
    grouped = df.groupby(['time'])
    data_obs = []
    for index, group_item in enumerate(grouped): 
        new_df = pd.DataFrame(index=[i for i in range(0,41)], columns=[i for i in range(0,64)]).fillna(0)
        grouped_df = group_item[1].rename(columns={Pollutant:'Pollutant'})[['Pollutant', 'x', 'y']]
        for index, row in grouped_df.iterrows():
            new_df[row['x']][row['y']] = row['Pollutant']
        data_obs.append(new_df.values)
    result = np.array(data_obs)
    return result

# Assigning the pollutant value to the grid coordinates
def final_data(Pollutant,whole_data, Date_time):
    d = whole_data[Date_time]
    obs_data = Obs_mapdata(Pollutant, Date_time)
    dic = {}
    for i in range(0,13):
        dic[i] = coordinate_data()
        for j in dic[i]:
            j['pollutant'] = d[i][j['y']][j['x']]
            j['Obs_con'] = obs_data[i][j['y']][j['x']]
    return dic

# Getting the final data for plotting the map
def map_data(Method,Pollutant,Date_time):
    if Method == 'CMAQ':
        root_dir = 'data/CMAQ/' + Pollutant
        pol_data = get_pollutant_data(root_dir)
    else:
        root_dir ='data/Our_method/' + Pollutant
        pol_data = get_pollutant_data(root_dir)
    whole_data = data(pol_data)
    final_data_ = final_data(Pollutant, whole_data, Date_time)
    df = pd.DataFrame.from_records(final_data_)
    f = df.to_json(orient='records')
    return f

      #########################################################################################################
    
# Code for plotting the line chart

# Station name with grid coordinates
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

# Getting data from CMAQ and our method for time range
def method_linedata(code, polu, start_date, end_date, Future_hour):
    # variables
    st_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(Future_hour))
    en_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=int(Future_hour))
    delta = en_date - st_date
    days, seconds = delta.days, delta.seconds
    hours = days * 24 + seconds // 3600
    coords = station_coord(code)
    
    df_list = []
#     for i in ['CMAQ', 'Our_Method']
    for i in ['CMAQ']:
        root_dir = 'data/'+ i + '/' + polu
        pol_data = get_pollutant_data(root_dir)
        whole_data = data(pol_data)
        date_list = [str(st_date + timedelta(hours=i)) for i in range(hours +1)]
        pol_lis = [whole_data[i][int(Future_hour)][coords[0]][coords[1]] for i in date_list]
        df = pd.DataFrame({'time': date_list, 'pollutant': pol_lis})
        df['data'] = i + '_data'
        df_list.append(df)
    return df_list

# Getting data from observatory station for time range
def Obs_linedata(code, polu, start_date, end_date, future_hour ):
    df = pd.read_csv('data/obs/' + code +'.csv', usecols=['time',polu])
    df['time']= (pd.to_datetime(df['time']) + pd.Timedelta(hours=8)).dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
    df['data'] = 'Obs_data'
    df.rename(columns={polu: 'pollutant'},inplace = True)
    return df

# Getting the metrics value 
def metrics(df_1, df_2):
    act = df_1['pollutant'].values
    pred = df_2['pollutant'].values
    rmse = round(sqrt(mean_squared_error(act, pred)),2)
    ioa = round(1 -(np.sum((act-pred)**2))/(np.sum((np.abs(pred-np.mean(act))+np.abs(act-np.mean(act)))**2)), 2)
    return rmse, ioa

# Combining all the data needed for line_chart_1
def data_lineChart_1(dt):
    Code = dt['St_code']
    Polu = dt['pollutant']
    Start_date = dt['st_date']
    End_date = dt['en_date']
    Future_hour = dt['F_hour']
    df_list = method_linedata(Code, Polu, Start_date, End_date, Future_hour)
    obs_df = Obs_linedata(Code, Polu, Start_date, End_date, Future_hour)
    RMSE, IOA = metrics(df_list[0], obs_df)
    df = pd.concat([df_list[0],obs_df])
    result = df.to_dict('records')
    return json.dumps([{'RMSE': RMSE, 'IOA': IOA, 'line_data': result}])