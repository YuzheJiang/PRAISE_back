from datetime import datetime, timedelta
from dateutil import tz
from glob import glob
import pandas as pd
import numpy as np
import json
import os

time = np.load('data/time_full.npy')

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
    time_data = [UTC2HKT(x) for x in time]
    np.save("data/cache/time_data.npy", time_data)
    return None

# Save the monthwise data
def save_data(pollutant_data, direc):
    time_data = np.load("data/cache/time_data.npy")
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
    for i in ['PM10', 'SO2', 'NO2']:
        directory = os.path.join('data',method, i)
        new_directory = os.path.join('data','cache',method, i)
        if not os.path.exists(new_directory):
            try:
                os.makedirs(new_directory)
            except:
                continue
        pol_data = get_pollutant_data(directory)
        start_time = datetime.now()
        save_data(pol_data,new_directory)
        end_time = datetime.now()
        print(end_time -  start_time)
    return None

# Combine and save the observatory data
def save_Obsdata():
    files = sorted(glob('data/obs/*.csv'))
    df = pd.concat((pd.read_csv(file, index_col=0)for file in files), ignore_index = True)
    df['time'] =  pd.to_datetime(df['time'])
    df.sort_values(by=['time', 'station_code'])
    if not os.path.exists('data/cache/obs'):
        os.makedirs('data/cache/obs')
    df.to_csv("data/cache/obs/Obs_data.csv", index=False)
    return df

if __name__ == '__main__':
    save_timedata()
    print("save_timedata done !!!")
    save_Obsdata()
    print("save_Obsdata done !!!")
    splitData_monthwise('CMAQ')
    print("CMAQ done !!!")
    splitData_monthwise('Our_method')
    print("Our_method done !!!")
    