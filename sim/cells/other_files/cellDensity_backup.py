#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 13:22:51 2019

@author: ricky
"""

'''


Script to obtain cell densities for different layers and cell types 
BASED ON M1 model (mouse) [cells/cellDensity.py]

'''

import numpy as np
from scipy.io import loadmat, savemat
from pprint import pprint
from scipy import interpolate
from pylab import *
from pprint import pprint
from netpyne import specs
import pickle

# --------------------------------------------------------------------------------------------- #
# MAIN SCRIPT
# --------------------------------------------------------------------------------------------- #

density = {}

## cell types
cellTypes = [   'E_VPL', 
                'E_VPM', 
                'E_POm', 
                'E_RTN', 
                'I_VPL', 
                'I_VPM', 
                'I_POm', 
                'I_RTN'] 

# ------------------------------------------------------------------------------------------------------------------
# 1) Use neuron density profile from 3D Quantification paper (Kelly & Hawken 2017) --> neurons/mm3
# Avg for L1, L2/3, L4, L5A, L5B, L6 from fig 6d
# ------------------------------------------------------------------------------------------------------------------
### Add VL because is important for M1
VPL = 0.83100*(10**5) # unknown - estimated equal as VPM ->83.100 +/- 7900 cells/mmˆ3 
VPM = 0.83100*(10**5) # 83.100 +/- 7.900 cells/mmˆ3 
POm = 0.41477*(10**5) # 41.477 +/- 3.612 cells/mmˆ3 
RTN = 0.49680*(10**5) # 49.680 +/- 1.097 cells/mmˆ3 

VPL_EI_ratio = [0.8,0.2]
VPM_EI_ratio = [0.8,0.2]
POm_EI_ratio = [0.8,0.2]
RTN_EI_ratio = [0,1.0]

# Cell density source: 2013, Meyer, PNAS - https://doi.org/10.1073/pnas.1312691110
density['nrn_density'] = [  VPL,  # VPL - Estimated to be equal VPM 
                            VPM,  # VPM
                            POm,  # POm
                            RTN]  # RTN
                            
# density['nrn_density'] = [  VPL*VPL_EI_ratio[0],  # VPL - Exc
#                             VPM*VPM_EI_ratio[0],  # VPM - Exc
#                             POm*POm_EI_ratio[0],  # POm - Exc
#                             RTN*RTN_EI_ratio[0],  # RTN - Exc
#                             VPL*VPL_EI_ratio[1],  # VPL - Inh
#                             VPM*VPM_EI_ratio[1],  # VPM - Inh
#                             POm*POm_EI_ratio[1],  # POm - Inh
#                             RTN*RTN_EI_ratio[1]]  # RTN - Inh 

# see:  Thal:   https://docs.google.com/spreadsheets/d/1Rj1y3CtjVqjJDDDAL6M6lzGS6aR5kS5MGQdBnonV9UQ/edit#gid=2005388318
#       A1:     https://docs.google.com/spreadsheets/d/1rXU6ujzg6TBG59XEFuyE1HTJ6VWM-Jr9XIjMMOxvU1g/edit#gid=460197992



# ------------------------------------------------------------------------------------------------------------------
# 2) Percentage of Excitatory Cells [from Lefort09 (mouse S1)]
# Avg for L2/3, L5A, L5B, L6 from fig 2D 
# overall 85:15 ratio consistent with Markram 2015 (87% +- 1% and 13% +- 1%) -->> Again is this percentage or ratio? 
# This is taken from M1 model cellDensity.py & modified 
# -------------------------------------------------------------------------------------------------------------------
#ratioEI = {}
#ratioEI['Lefort09'] = [(0.193+0.11)/2, 0.09, 0.21, 0.21, 0.10]
percentE = {}
percentE['EIratio'] = [0.8,0.8,0.8,0] # IMPROVE - needs references
density[('thal','E')] = [round((density['nrn_density'][i] * percentE['EIratio'][i])) for i in range(len(density['nrn_density']))] # keep in mind this is number of excitatory cells / (mm^3)
density[('thal','I')] = [round((density['nrn_density'][i] * (1-percentE['EIratio'][i]))) for i in range(len(density['nrn_density']))] 

# density[('thal','E')] = [round(density['nrn_density'][i]) * (percentE['EIratio'][i]) for i in range(len(density['nrn_density']))] # keep in mind this is number of excitatory cells / (mm^3)
# density[('thal','I')] = [round(density['nrn_density'][i]) * (1-percentE['EIratio'][i]) for i in range(len(density['nrn_density']))] 

# # ------------------------------------------------------------------------------------------------------------------
# # 3) Use interneuron proportions from 'GABAergic interneurons in neocortex' (Tremblay et al., 2016)
# # Avg for PV, SOM, VIP, non-VIP in each layer of mouse somatosensory cortex (fig 2)
# # ------------------------------------------------------------------------------------------------------------------
# PV = 	[0.007, 0.29, 0.641, 0.54, 0.465, 0.424]       # L1: 0.7% (0.007)
# SOM = 	[0.04, 0.116, 0.169, 0.319, 0.389, 0.318]      # L1: 4% (0.04)
# VIP = 	[0.052, 0.347, 0.092, 0.078, 0.06, 0.064]      # L1: 5.2% (0.052)
# nonVIP = [0.9, 0.247, 0.099, 0.064, 0.085, 0.193]      # L1: 90% (0.9)

# # Keep in mind again that all of these numbers are /mm3
# density[('A1','PV')] =     [(density[('A1','I')][i])*(PV[i]) for i in range(len(PV))] 
# density[('A1','SOM')] =    [(density[('A1','I')][i])*(SOM[i]) for i in range(len(SOM))]
# density[('A1','VIP')] =    [(density[('A1','I')][i])*(VIP[i]) for i in range(len(VIP))]
# density[('A1','nonVIP')] = [(density[('A1','I')][i])*(nonVIP[i]) for i in range(len(nonVIP))]


print(density)

# save density data in pickle object 
savePickle = 1

data = {'density': density}

if savePickle:
    with open('cellDensity.pkl', 'wb') as fileObj:        
        pickle.dump(data, fileObj)

