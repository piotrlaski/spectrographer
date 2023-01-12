"""
Created on Thu Feb 11 18:40:20 2021

@author: piotr

This script can quickly cut logs in datasets in order to remove frames in which the crystal is already dead. Just point the general directory of the datasets. Using the create_file function first, you can create a template for the intended cutoffs "CutThese.txt", which will be used to cut logfiles with cut_files function (always leave one of these functions commented!). The newly created logfiles will be appended with '_cut.log' appendix.
"""

import os

def create_file(cutDir):
    '''
    Creates an empty file listing all possible logfiles in submitted directory
    Usage::
    path cutDir :: path for scanned directory
    '''
    logFiles = []
    for root, dirs, files in os.walk(cutDir):
        for i in files:
            if i[-4:] == '.log' and i[:4] != 'dark':
                logFiles.append(os.path.join(root, i))
    
    f = open (os.path.join(cutDir, 'CutThese.txt'), '+w')
    for i in logFiles:
        f.write(str(i))
        f.write(' \n')
    f.close()
    return

def read_cuts(cutDir):
    '''
    Reads a CutThese.txt file in the selected directory and returns its arrays for log paths and corresponding frame cuts
    Usage::
    path cutDir :: path for directory containing CutThese.txt and laser logfile subdirectories
    '''
    logPath = []
    logCut = [] 
    f = open (os.path.join(cutDir, 'CutThese.txt'))
    for i in f.readlines():
        logPath.append(i.split()[0])
        logCut.append(i.split()[1])
    f.close()
    return logPath,logCut

def cut_files(cutDir, wasteLines = 19):
    '''
    Cuts all laser log files in the subdirectories of cutDir. CutThese.txt containing info about each logfile path and its cutoff frame required (whitespace delimited, newline after each pair)
    Usage::
    path cutDir :: path for directory containing CutThese.txt and laser logfile subdirectories
    int wasteLines :: number of non-frame lines at the beggining of each logfile
    '''
    logPath, logCut = read_cuts(cutDir)
    for i in range (len(logPath)):
        f = open (logPath[i])
        logFile = f.readlines()
        f.close
        print (logPath[i])
        print ('Leaving frames 1-' + str(logCut[i]) +  ' out of ' + str(len(logFile) - wasteLines))
        out = open (logPath[i][:-4] + '_cut.log', 'w+')
        for j in range (0, wasteLines + int(logCut[i])):
            out.write(logFile[j])
        out.close()        

cutDir = 'E:\\Processing\\CuDPPE_Testing'
#create_file(cutDir)
cut_files(cutDir)



