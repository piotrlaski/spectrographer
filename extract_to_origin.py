import os
import pandas as pd

dir = r'C:\Users\piotr\Documents\VS_Code\working_dirs\old_AM\11_07_23_AM_0001_100K\out'

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

for subdir in listdir_fullpath(dir):
    if os.path.isdir(subdir):
        for object_path in os.listdir(subdir):
            if object_path[:12] == 'TimeResolved':
                file_path = os.path.join(subdir, object_path)
                data = pd.read_csv(
                    file_path,
                    sep = ' ',
                    header = None,
                    names = ['A', 'B', 'C', 'D'])
                data = data.drop(['B', 'D'], axis = 1)
                data = data.drop([0], axis = 0)
                data['A'] = data['A'] / 1000
                data['C'] = data['C'] / data['C'].max()

                sample_name = os.path.split(subdir)[1]
                wavelength = file_path[-7:-4]
                new_file_path = os.path.join(subdir, f'{sample_name}_{wavelength}.csv')
                data.to_csv(new_file_path, encoding='utf-8', index=False, header=False, sep=' ')

