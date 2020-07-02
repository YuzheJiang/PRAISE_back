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
            cell_x =j
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
    result.rename(columns={filter_col: "pollutant"}, inplace = True)
    feature = coordinate_data()
    merge_df = pd.merge(feature, result,  how='left', on =['x', 'y'])
    data = merge_df.to_json(orient='records')
    return data

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