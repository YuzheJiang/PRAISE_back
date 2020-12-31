from datetime import datetime, timedelta
from dateutil import tz
from glob import glob
import pandas as pd
import numpy as np
import json
import os


def get_pollutant_data(dir):
    return np.load(dir + "_full.npy")
    
# Formula for the timestamp conversion(UTC to HKT)
def UTC2HKT(timestamp):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Hong_Kong')
    fmt = '%Y-%m-%d %H:%M:%S'

    HK_T = datetime.strptime(str(datetime.utcfromtimestamp(float(timestamp))),
                            '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone)\
                            .astimezone(to_zone).strftime(fmt)
    return HK_T

# Convert UTC time to HK time and save as .npy file
def save_timedata():
    for i in ['CMAQ', 'Model']:
        time = np.load('data/time_full_'+i+'.npy')
        time_data = [UTC2HKT(x) for x in time]
        np.save('data/cache/time_data_'+i+'.npy', time_data)
    
    base_time = datetime(2018, 1, 2, 21)
    datetime_list = np.array([(base_time + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(8700)])
    np.save('data/cache/time_data_CMAQ_2018.npy', datetime_list)
    return None

# Save the monthwise data
def save_data(pollutant_data, direc, yr):
    method = direc.split('/')[-2]
    if method == 'CMAQ' and yr == '2017':
        time_data = np.load("data/cache/time_data_CMAQ.npy")
    elif method == 'CMAQ' and yr == '2018':
        time_data = np.load("data/cache/time_data_CMAQ_2018.npy")
    elif method == 'Our_method' and yr == '2017':
        time_data = np.load("data/cache/time_data_Model.npy")
    else:
        time_data = np.load("data/cache/time_data_Model.npy")
    print(time_data)
    for i in range(0,12): 
        data = []
        first_date = next(x for x in time_data if datetime.strptime(x, '%Y-%m-%d %H:%M:%S').month == i+1)
        for x,j in zip(time_data,pollutant_data):
            date = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
            if date.month == i+1 :
                data.append(j)
        np.save(os.path.join(direc, first_date + ".npy"), data)
    return None

# Split the data into monthwise
def splitData_monthwise(method):
    for year in os.listdir('data/'+ method):
        if year.startswith('.') == False:
            print(year)
            for i in ['PM10', 'SO2', 'NO2', 'O3', 'PM25']:
                directory = os.path.join('data',method,year,i)
                new_directory = os.path.join('data','cache',method,i)
                if not os.path.exists(new_directory):
                    try:
                        os.makedirs(new_directory)
                    except:
                        continue
                pol_data = get_pollutant_data(directory)
                start_time = datetime.now()
                save_data(pol_data,new_directory,year)
                end_time = datetime.now()
                print(end_time -  start_time)   
    return None

# Combine and save the observatory data
def save_Obsdata():
    df_list = []
    for file in os.listdir('data/obs/'):
        if not file.startswith('.'):
            files = sorted(glob('data/obs/'+file+'/*.csv'))  
            df = pd.concat((pd.read_csv(file, index_col=0)for file in files), ignore_index = True)
            if file == '2017':
                df['time'] =  pd.to_datetime(df['time']) + pd.to_timedelta(8, unit='h')
            else: 
                df['time'] = pd.to_datetime(df['time'],unit='s') + pd.to_timedelta(8, unit='h')
            df.sort_values(by=['time', 'station_code'])
            df = df[['time','station_code','x','y','NO2','O3','PM10','PM25','SO2']]
            df_list.append(df)
    if not os.path.exists('data/cache/obs'):
        os.makedirs('data/cache/obs')
    data_frame = pd.concat(df_list)
    data_frame.to_csv("data/cache/obs/Obs_data.csv", index=False)
    return None

if __name__ == '__main__':
    # save_timedata()
    # print("save_timedata done !!!")
    # save_Obsdata()
    # print("save_Obsdata done !!!")
    # splitData_monthwise('CMAQ')
    # print("CMAQ done !!!")
    splitData_monthwise('Our_method')
    print("Our_method done !!!")
    