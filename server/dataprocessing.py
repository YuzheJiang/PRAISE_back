import pandas as pd

root_dir = 'data/data_1.csv'
latExtent = [22.16,22.5277]
lonExtent = [113.816, 114.442]
cellCount = [41, 64]
cellSizeCoord = [0.01, 0.009]

def read_csv_file(dir):
    ''' Reads a csv file and returns a dataframe'''
    df = pd.read_csv(dir)
    return df

def coordinate_data():
    Features = []
    for i in range(0,cellCount[0]):
        cell_y = i
        for j in range(0, cellCount[1]):
            rect ={"type": 'polygon', "x": None ,"y": None , "coord":[]}
            cell_x =j;
            bottomLeft = [latExtent[0] + cellSizeCoord[1]*i, lonExtent[0] + cellSizeCoord[0]*j]
            bottomRight = [bottomLeft[0], bottomLeft[1] + cellSizeCoord[0]]
            topLeft = [bottomLeft[0]+ cellSizeCoord[1], bottomLeft[1]]
            topRight = [bottomRight[0]+ cellSizeCoord[1],bottomRight[1]]
            coords = [bottomLeft, bottomRight, topRight, topLeft]
            rect["x"], rect["y"], rect["coord"] = cell_x, cell_y, coords
            Features.append(rect)
    df = pd.DataFrame.from_records(Features)
    return df

def get_pollutant_data(filter_col):
    ''' Filters dataframe column corresponding to users preference on pollutants'''
    df = read_csv_file(root_dir)
    result = pd.concat([df.iloc[:, :4 ], df[filter_col]], axis=1).drop(['lon','lat'], axis =1)
    feature = coordinate_data()
    merge_df = pd.merge(feature, result,  how='left', on =['x', 'y'])
    data = merge_df.to_json(orient='records')
    return data
