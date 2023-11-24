# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 15:34:55 2023

@author: piotr
"""

import os
import numpy as np

csv_path = 'C:\\Users\\piotr\\Desktop\\100K\\rt\\out\\frames'
out_path = os.path.split(csv_path)[0] + 'out_analysis.csv'


wls_loaded = False
for csv in os.listdir(csv_path):
    current_frame_path = os.path.join(csv_path,csv)
    data = np.loadtxt(current_frame_path)
    if not wls_loaded:
        wls = data[:,1]
        data_output = np.append(0, wls)
        data_output = np.expand_dims(data_output, 1)
        wls_loaded = True
    current_delay = data[0][0]
    intensities = data[:,2]
    frame_data = np.append(current_delay, intensities)
    
    frame_data = np.expand_dims(frame_data, 1)

    data_output = np.concatenate([data_output, frame_data], axis = 1)
        
np.savetxt(out_path ,data_output.astype(float), fmt='%.9e', delimiter=',')
    
