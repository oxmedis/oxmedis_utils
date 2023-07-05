# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 13:36:53 2023

@author: jamhby
"""

import pydicom as dicom
import numpy as np
from scipy import ndimage
import cv2

#Determine snip points by variance thresholding:
#Idea is that if a row contains image and background then that row will have a variance above a certain threshold

#utility to convert dicom to np array and convert to [0, 255]
def dcm_to_npy(dcm):
    imarray = dicom.dcmread(dcm).pixel_array
    imarray = imarray/np.max(imarray)
    imarray *= 255
    imarray = np.round(imarray)
    return imarray

#Function to crop image by variance thresholding, probably superseded by new snip_axis() function
def crop_axis(img, axis, thresh=10):
    #Filtering invalid inputs
    if img is None:
        return None
    if 0 in img.shape:
        return None
    
    #Variance thresholding along axis
    S = np.std(img, axis=axis)
    Bin_S = S
    Bin_S[np.where(Bin_S<thresh)]=0
    Bin_S[np.where(Bin_S!=0)]=1
        
    #If we somehow have a blank image, exit
    if np.sum(Bin_S) == 0:
        return None

    #Remove Leading and end BG along axis
    start = np.min(np.where(Bin_S==1))
    end = np.max(np.where(Bin_S==1))
    if axis==0:
        img = img[:, start:end]      
    if axis==1:
        img = img[start:end, :]
            
    return img

#Utility function to crop stubborn images
#Repeats because the crop order matters in some cases
def trim(img):
    return crop_axis(crop_axis(crop_axis(crop_axis(img, 0, 10), 1, 10), 0, 10), 1, 10)

#Function to snip along given axis, theoretically extracts all xrays separated by background
def snip_axis(img, axis, thresh=10, window=1):
    #Create Flag to indicate if a snip fails
    errflag = 0
    
    if window != 1:
        win_val = (1-window)/2
        win_start = int(img.shape[axis]*win_val)
        win_end = int(img.shape[axis]*(1-win_val))
    
        #Window image to remove confounding edge
        if axis == 0:
            windowed_im = img[win_start:win_end, :]
        if axis == 1:
            windowed_im = img[:, win_start:win_end]
        
        #plt.figure()
        #plt.imshow(windowed_im)
    else:
        windowed_im = img
    
    #Standard variance check
    S = np.std(windowed_im, axis=axis)
    Bin_S = S
    Bin_S[np.where(Bin_S<thresh)]=0
    Bin_S[np.where(Bin_S!=0)]=1
    
    #Use ndimage.label to label connected regions
    m, nf = ndimage.label(Bin_S)
    u, c = np.unique(m[np.where(m!=0)], return_counts=True)
    #[COULD BE IMPROVED] Check for region size and keep only regions > 10% of overall size
    for n, val in enumerate(c):
        if val/img.shape[1-axis] < 0.1:
            m[np.where(m==u[n])]=0 
    u, c = np.unique(m[np.where(m!=0)], return_counts=True)
    if len(u)==0:
        return [img], errflag

    #If the biggest region is > 80% of overall size then flag as error for subsequent analysis
    if np.max(c/img.shape[1-axis]) >0.8:
        errflag = 1
    
    #Extract remaining regions as separate images
    ims = []
    for ele in u:
        if axis==0:
            ims.append(img[:, np.min(np.where(m==ele)):np.max(np.where(m==ele))])
        if axis==1:
            ims.append(img[np.min(np.where(m==ele)):np.max(np.where(m==ele)), :])
            
    return ims, errflag
        
#Legacy utility function to remove stubbon artefacts, function should be superseded by snip_axis()
def fix_horiz(img, thresh=10):
    h, w = img.shape
    S = np.std(img, axis=0)
    Bin_S = S
    Bin_S[np.where(Bin_S<thresh)]=0
    Bin_S[np.where(Bin_S!=0)]=1
    
    m, nf = ndimage.label(Bin_S)
    u, c = np.unique(m[np.where(m!=0)], return_counts=True)
    val = u[np.argmax(c)]
    
    m[np.where(m!=val)]=0
    m[np.where(m==val)]=1
        
    start = np.min(np.where(m==1))
    end = np.max(np.where(m==1))
    img = img[:, start:end]  
    
    
    return img

#function to apply the snips and collect the output
def quarter(img):
    
    w, h = img.shape
        
    #Try to keep all images w/ white bone
    if img[0, h//2] > 250:
        img = 255-img
            
    img = trim(img)
    if img is None:
        return None, 'N'
            
    #Filter for single scan images
    w1, h1 = img.shape
    if w1 < 1000 or h1 < 1000:
        #Then Single Scan
        #print('S')
        #Do Single Scan output
        return [img], 'S'
    
    #Crop once more to remove leading/trailing BG
    img = trim(img)
    #Split along x (requiring strict zero variance)
    imarrays, errorx = snip_axis(img, axis=0, thresh=5)
    if errorx == 1:
        imarrays, errorx = snip_axis(img, axis=0, thresh=5, window=0.8)
                
    finalims = []
    for idx1, array in enumerate(imarrays):
        f_ims, errory = snip_axis(array, axis=1, thresh=10)
        if errory == 1:
            f_ims, errory = snip_axis(array, axis=1, thresh=5, window=0.8)
        for idx2, f_im in enumerate(f_ims):
                
            f_im = trim(f_im)

            #Try and ensure bone is white:
            u, c = np.unique(f_im, return_counts=True)
            if u[np.argmax(c)] > 200:
                f_im = 255-f_im
            
            finalims.append([f_im, [errorx, errory]])

    return finalims, 'NS'

def error_check(ims, n_ims):
    titlestring = 'correct'
    
    outims = []
    for im in ims:
        img = im[0].astype('uint8')
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img = clahe.apply(img)
        _,img = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        u, c = np.unique(img, return_counts=True)
        c = c/np.sum(c)
        #plt.figure()
        #plt.title(c)
        #plt.imshow(img)
        if c[0]<0.82 and c[1]<0.82:
            outims.append(im)
    
    ims = outims
    if len(ims)==3 or len(ims)==1 and n_ims==1:
        titlestring = 'error'
                
    for i, im in enumerate(ims):
        err = im[1]
        im = im[0]
        im = trim(im)
                
        ratio = np.round(im.shape[1]/im.shape[0], 3)
        A = im.shape[0]*im.shape[1]/10000
        if ratio > 1.1 or A>400 and imname not in errornames:
            titlestring = 'error'
            
    return titlestring, ims