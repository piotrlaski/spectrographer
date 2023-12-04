# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 14:24:33 2021

@author: Piotr
"""

import os
from scipy.interpolate import interp1d
import matplotlib.pylab as plt
from oper import origin_fit_decay
import re


def sorting_key(x):
    return (x[:-4])

def infoRead(path):
    """
    Extracts data from LightField infofiles.
    
    Parameters
    ----------
    path : str    

    Returns:
    double gateStart : absolute time of the first measured frame (in ns)
    double gateEnd : absolute time of the last measured frame (in ns)
    int frames : number of frames in the dataset
    double gateStartWidth : starting gating width (in ns)
    double gateEndWidth : ending gating width (in ns)
    int CCD : number of on-CCD accumulations
    int avgFrames : number of averaged measurements for each frame
    int intesifier : intensifer setting
    int xSteps : number of X-axis (wavelength) steps in each frame

    
    """

    f = open(path)
    content = f.read()
    f.close()
      

    def unit_mutliplier(unit_string):
        if ord(unit_string) == 181:
            return 1000
        elif ord(unit_string) == 109:
            return 1000000
        else:
            return 1
    
    starting_gate_string = re.findall('Starting Gate.*', content)[0][22:].split()
    ending_gate_string = re.findall('Ending Gate.*', content)[0][20:].split() 
    gateStart = float(starting_gate_string[0]) * unit_mutliplier(starting_gate_string[1][-3])
    gateStartWidth = float(starting_gate_string[3]) * unit_mutliplier(starting_gate_string[4][-2])
    gateEnd = float(ending_gate_string[0]) * unit_mutliplier(ending_gate_string[1][-3])
    gateEndWidth = float(ending_gate_string[3]) * unit_mutliplier(ending_gate_string[4][-2])
    

    #Frame number
    frames = ''
    index = content.index('Frames to Save') + 16
    while (content[index].isdigit() or content[index] == '.'):
        frames = frames + content[index]
        index = index + 1
   
    #CCD
    CCD = ''
    index = content.index('On-CCD Accumulations') + 22
    while (content[index].isdigit() or content[index] == '.' or content[index] == ','):
        CCD = CCD + content[index].replace(',' ,'')
        index = index + 1
    
    #AvgFrames
    avgFrames = ''
    index = content.index('Exposures per Frame') + 21
    while (content[index].isdigit() or content[index] == '.'):
        avgFrames = avgFrames + content[index]
        index = index + 1
        
    #Intensifier
    intensifier = ''
    index = content.index('Intensifier Gain') + 18 
    while (content[index].isdigit() or content[index] == '.'):
        intensifier = intensifier + content[index]
        index = index + 1
        
    #X-axis multiplicity
    xSteps = ''
    index = content.index('Data Block, Region') + 20
    while (content[index].isdigit() or content[index] == '.'):
        xSteps = xSteps + content[index]
        index = index + 1
    
    print ((gateStart), (gateEnd), (frames), (gateStartWidth), (gateEndWidth), (CCD), (avgFrames), (intensifier), (xSteps))
    
    return (float(gateStart), float(gateEnd), int(frames), float(gateStartWidth), float(gateEndWidth), int (CCD), int(avgFrames), int(intensifier), int(xSteps))

def loadCSV(path):
    '''
    Simply loads an csv file into a 2D list

    '''
    f = open(path)
    content = []
    while line := f.readline():
        content.append((line[:-1]).split())
    f.close()
    for i in range (len(content)):
        for j in range (len(content[0])):
            content[i][j] = float(content[i][j])
    return content

def frameToTime(csvArr, gateStart, gateEnd, frames, xSteps):

    """
    Converts frames to absolute time in 2D list imported from csv files.
    Returns a converted 2D list
    """    
    
    step = (gateEnd - gateStart)/(frames-1)
    for j in range (frames):
        for i in range (xSteps):
            csvArr[j * xSteps + i][0] = gateStart + j * step
    return (csvArr)

def rescaleNorm(csvArr, timeNorm, wlNorm, intNorm):
    '''
    Rescales entire dataset's intensity so that it is consistent with a single dataplace in timeNorm, wlNorm

    '''
    norm = 0.0
    for i in range (len(csvArr)):
        if csvArr[i][0] == timeNorm and csvArr[i][1] == wlNorm:
            norm = intNorm/csvArr[i][2] 
    csvArrRescaled = csvArr
    for i in range (len(csvArrRescaled)):
        csvArrRescaled[i][2] = csvArrRescaled[i][2] * norm
        
    print ('Stiching norm is ', norm)
    return csvArrRescaled

def mergeArr(csvArr1, csvArr2):
    '''
    Merges 2 arrays. csvArr2 comes after csvArr1.
    '''
    for i in csvArr2:
        csvArr1.append(i)   
    return csvArr1
    
def relTime(csvArr, t0):
    '''
    Subtracts t0 from the first column in csvArr, making timestamps relative to t0
    '''
    for i in range(len(csvArr)):
        csvArr[i][0] = csvArr[i][0] - t0
    return csvArr

def normSearch(csvArr, frames, xSteps, wl):
    '''
    Finds the intensity of a last two frames in a given WL in a given csvArray (useful for using rescaleNorm())
    '''
    normLine = [] 
    for i in range ((frames-2)*xSteps, frames*xSteps):
        if csvArr[i][1] == wl:
            normLine.append(csvArr[i])
    return normLine

def normArr(csvArr, norm = 0.0):
    '''
    Normalizes the array to the specified intensity or to the max intensity otherwise
    '''
    if norm == 0.0:
        norm = max(i[2] for i in csvArr)
    for i in range(len(csvArr)):
        csvArr[i][2] = csvArr[i][2]/norm
    print ('Overall norm is: ', norm)
    return csvArr

def extractWL(csvArr, wl):
    '''
    Extracts data for a single wavelength (time resolved data)
    '''
    timeResolved = []
    for i in csvArr:
        if i[1] == wl:
            timeResolved.append(i)
    return timeResolved

def findMaxWL(csvArr, n = 3):
    '''
    Finds max WL and t0 of dataset
    '''
    
    
    maxVal = max(i[2] for i in csvArr)
    j = []
    for i in csvArr:
        if i[2] == maxVal:
            j = i
    print ('Max Wavelength found at: ', j[1], ' nm at time0 = ', j[0], ' ns')
    maximal_wls = []
    prev_time = 0
    cur_max = [0, 0, 0]
    for i in csvArr:
        if i[0] != prev_time:
            prev_time = i[0]
            maximal_wls.append(cur_max[1])
            cur_max = i
            continue
        if i[2] > cur_max[2]:
            cur_max = i
    maximal_wls.append(cur_max[1])
    maximal_wls.pop(0)
    maximal_wls = maximal_wls[:int(len(maximal_wls) / n)]
    maximal_wls_avg = sum(maximal_wls) / len(maximal_wls)
    avg_max_wl = min(maximal_wls, key = lambda x: abs(x - maximal_wls_avg))
    
    print (f'Average max WL for the first 1/{n} of frames is {avg_max_wl} nm')
    return avg_max_wl,j[0]

def writeCSV(csvArr, path):
    '''
    Saves a CSV file of a given array in a given path (with file name and extension)
    '''    
    f = open (path, 'w+')
    for i in csvArr:
        for j in i:
            f.write(str(j) + ' ')
        f.write('\n')
    f.close()
    return
    
def divideFrames(csvArr, path, t0, xSteps, framesTotal):
    '''
    Divides the dataset into separate .csv files with each frame . Creates 'frames' dir in the specified path
    '''
    path = os.path.join(path, 'frames')
    if not os.path.exists(path):
        os.makedirs(path)
    for i in range (int(framesTotal)):
        f = open(os.path.join(path,str(csvArr[i * xSteps][0] + t0) + '.csv') ,'+w')
        for j in range (i * xSteps, i * xSteps + xSteps):
            f.write(str(csvArr[j][0]) + ' ' + str(csvArr[j][1]) + ' ' + str (csvArr[j][2]) + '\n')
        f.close()
    return
        
def plotStacked(framesPath, frameNums, title = '', max_wl = 1000):

    data = []
    for i in range(len(os.listdir(framesPath))):
        if i in frameNums:
            sort = sorted(os.listdir(framesPath), key=sorting_key)
            fullPath = os.path.join(framesPath, sort[i])
            data.append(loadCSV(fullPath))
    times = []
    for i in data:
        times.append(i[0][0])
        time = i[0][0]
        x = []
        y = []
        for j in i:
            x.append(j[1])
            y.append(j[2])
        if float(time) >= 1000:
            (plt.plot(x,y, label=('{0:.1f}'.format(float(time)/1000) + ' us')))
        else:
            plt.plot(x,y, label=('{0:.1f}'.format(float(time)) + ' ns'))
    
    plt.axvline(max_wl, linewidth=0.5, color='r', dashes = (5, 2, 1, 2))
    plt.ylim(0, 1.0)
    plt.xlim(400, 900)
    plt.title(title)
    plt.legend(loc="upper right")
    plt.savefig(os.path.join(os.path.split(framesPath)[0],title), bbox_inches='tight', dpi=300)
    plt.close()
    return data

def findCSV(path):
    '''
    spaghetti to find proper .csv and .txt files in a path
    '''
    onlyFiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    infoFile = [f for f in onlyFiles if f[-8:] == 'info.txt'][0]
    csvFile = [f for f in onlyFiles if (f[-4:] == '.csv')][0] #changed for single file, didnt work prev. (06.09.22)
    return (infoFile, csvFile)

def linExpol(t1, t2, int1, int2, t3, wl):
    '''
    Generates a list of linearly extrapolated valus for intensity at t3 at wl basing on these in t1,t2,int1,int2
    '''
    x = [t1, t2]
    y = [int1, int2]
    f = interp1d(x,y,fill_value="extrapolate")
    int3 = float("{:.2f}".format(float(f(t3))))
    return ([t3, wl, int3])

def rangeTR(arr, wl, rg):
    '''
    Creates a Time-resolved dataset with integrated range specified in rg frames around wl
    '''
    timeResolvedRange = []
    line = [0,0,0]
    for i in range (len(arr)):
        if arr[i][1] == wl:
            line[0] = arr[i][0]
            line[1] = arr[i][1]
            line[2] = 0
            for j in range(i - rg, i + rg):
                line[2] = line[2] + arr[j][2]
            timeResolvedRange.append(line[:])
    return timeResolvedRange

def make_spectra(path, path2 = None, path3 = None, outPath = None, merge = False, IRF_threshold = 2.0, n = 3, fit_function = 'ExpDec2', plot_without_adj = False):
    
    if outPath == None:
        outPath = path
    
    if not os.path.exists(outPath):
        os.mkdir(outPath)
    
    ###read the primary file
    
    info = infoRead(os.path.join(path, findCSV(path)[0]))
    content = loadCSV(os.path.join(path, findCSV(path)[1]))
    contentAbs = frameToTime(content, info[0], info[1], info[2], info[8])
    framesTotal = info[2]
    logFile = open(os.path.join(path,'parameters.txt'), '+w')
    for i in info:
        logFile.write(str(i) + '\n')
    logFile.close()
    
    ##read the secondary file, which will be stiched to the primary file (optional)
    
    if merge:
        info2 = infoRead(os.path.join(path2, findCSV(path2)[0]))
        content2 = loadCSV(os.path.join(path2, findCSV(path2)[1]))
        contentAbs2 = frameToTime(content2, info2[0], info2[1], info2[2], info2[8])
        framesTotal = framesTotal + info2[2]
        logFile = open(os.path.join(path2,'parameters.txt'), '+w')
        for i in info2:
            logFile.write(str(i) + '\n')
        logFile.close()


    ##read the tertiary file, which will be stiched to the primary file (optional)
    
    if merge:
        info3 = infoRead(os.path.join(path3, findCSV(path3)[0]))
        content3 = loadCSV(os.path.join(path3, findCSV(path3)[1]))
        contentAbs3 = frameToTime(content3, info3[0], info3[1], info3[2], info3[8])
        framesTotal = framesTotal + info3[2]
        logFile = open(os.path.join(path3,'parameters.txt'), '+w')
        for i in info3:
            logFile.write(str(i) + '\n')
        logFile.close()
        
    
    #find WL and t0 of highest intensity point. Alternatively, set wl and t0 manually
    maxes=findMaxWL(contentAbs, n)
    t0 = 46.5
    #t0 = 310822.0
    wl = maxes[0]
    #wl = 640.03527842334245
    
    
    #stiching (optional)
    if merge:
        # values = normSearch(contentAbs, info[2], info[8], wl)
        # linValues = [values[0][0], values[1][0], values[0][2], values[1][2], info2[0], values[0][1]]
        # normLine = linExpol(*linValues)
        # contentAbs2Rescaled = rescaleNorm(contentAbs2, normLine[0], normLine[1], normLine[2])
        mergedContent = mergeArr (contentAbs, contentAbs2)
        mergedContent = mergeArr (mergedContent, contentAbs3)
        contentAbs = mergedContent
        
    #make time stamps relative to t0
    contentAbs = relTime(contentAbs, t0)
    
    #make wide-range TR csv
    rg = 40   #div/4
    x = (rangeTR(contentAbs, wl, rg))
    x = normArr(x)
    writeCSV(x, os.path.join(outPath,'RangeTimeResolved_'+ str(wl)[:3] + '_' + str (round(rg/4)) +'.csv'))
    
    #normalize to unitary
    contentAbs = normArr(contentAbs)
    
    #divide frames into separate .csv files
    divideFrames(contentAbs,outPath, t0, info[8], framesTotal)
    
    #plot stacked graph
    title = os.path.split(outPath)[1]
    plotStacked(os.path.join(outPath,'frames'), [0,2,5,20,50], title, max_wl = wl)
    
    #export a wavelength and write to 
    timeResolved = extractWL(contentAbs, wl)
    
    #without IRF correction:
    if plot_without_adj:
        writeCSV(timeResolved, os.path.join(outPath,'TimeResolved_'+ str(wl)[:3] + '.csv'))
        origin_fit_decay(wavelength = str(wl)[:3], unit = 'ns', title = title, csv_path = os.path.join(outPath,'TimeResolved_'+ str(wl)[:3] + '.csv'))

    #with IRF correction:
    time_resolved_IRF = []
    for x in timeResolved:
        if x[0] > IRF_threshold:
            time_resolved_IRF.append(x)
    
    IRF_norm = max([x[2] for x in time_resolved_IRF])
    
    time_resolved_IRF = [[x[0], x[1], x[2] / IRF_norm] for x in time_resolved_IRF]     
    
    writeCSV(time_resolved_IRF, os.path.join(outPath,'TimeResolved_IRF_'+ str(wl)[:3] + '.csv'))
    origin_fit_decay(wavelength = str(wl)[:3],
               unit = 'ns',
               title = 'IRF_' + title,
               csv_path = os.path.join(outPath,'TimeResolved_IRF_'+ str(wl)[:3] + '.csv'),
               fun = fit_function)
    return
    

path = os.path.normpath(r'C:\Users\piotr\Documents\VS_Code\working_dirs\old_AM\11_07_23_AM_0001_100K\short')
path2 = os.path.normpath(path[:-5] + 'mid')
path3 = os.path.normpath(path[:-5] + 'long')
outPath = os.path.normpath(path + '_out')


merge = True       ## False if single file, True if two files
IRF_threshold = 2.0  ## Subtract IRF-contaminated frames up to this time in ns
n = 6  # 1/n frames will be taken into account when calculating the max WL
fit_function = 'ExpDec2'

if __name__ == '__main__':
    make_spectra(path, path2, path3, outPath, merge, IRF_threshold, n, fit_function = fit_function, plot_without_adj = False)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    