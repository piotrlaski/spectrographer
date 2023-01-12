# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 12:57:50 2021

@author: Piotr

This program Extracts .h5 and number_of_pairs.txt files from directory and subdirectories. Copies them into a selected place, names them parent2_parent1.h5 (or .nop)
"""

import os
from shutil import copyfile

scanDir = os.getcwd()
copyDir = 'E:\\Processing\\CuDPPE_Results'

def double_parent_name(path, appendix = ''):
    '''
    Returns a joint string of a second and first parent of a selected file, appended with a selected appendix
    usage::
    path :: path to a file
    str appendix :: appendix added at the end of the result (can be left empty)
    '''
     
    def parent(path):
        return (os.path.split(path)[0])
    
    def child(path):
        return (os.path.split(path)[1])
    
    return child(parent(parent(path))) + '_' + (child(parent(path))) + appendix

def extract_indices (scanDir, copyDir):
    '''
    Extracts .h5 and number_of_pairs.txt files from directory and subdirectories. Copies them into a selected place, names them parent2_parent1.h5 (or .nop)
    
    Parameters
    ----------
    scanDir : os.path
        path to the scanned directory.
    copyDir : os.path
        path to the destination directory.

    Returns
    -------
    None.

    '''
    for root, dirs, files in os.walk(scanDir):
        for i in files:
            if i == 'yyy.h5':
                file = os.path.join(root, i)
                copyfile (file, os.path.join(copyDir, double_parent_name(file, '.h5')))
            if i == 'number_of_pairs.txt' and os.path.split(root)[1][:5] == 'laser':
                file = (os.path.join(root, i))
                copyfile (file, os.path.join(copyDir, double_parent_name(file, '.nop')))
    return

extract_indices(scanDir, copyDir)