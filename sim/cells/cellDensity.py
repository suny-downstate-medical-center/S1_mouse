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

# ------------------------------------------------------------------------------------------------------------------
# Cell density values for each region of the Thalamus
# Main source: 2018, Keller, Frontiers in neuroanatomy - https://doi.org/10.3389/fnana.2018.00083
# 2013, Meyer, PNAS - https://doi.org/10.1073/pnas.1312691110
# ------------------------------------------------------------------------------------------------------------------

'''
# LITERATURE DATA 
# Motor innervation
VL = 0.52228*(10**5) # unknown - estimated equal as VPL(P21) Łuczyńska, 2003 ->52.228 +/- 3077 cells/mmˆ3 
VM = 0.52228*(10**5) # unknown - estimated equal as VPL(P21) Łuczyńska, 2003 ->52.228 +/- 3077 cells/mmˆ3 
# Somatosensory innervation
VPL = 0.52228*(10**5) # 52.228 +/- 3.077 - Łuczyńska, 2003 - Data from (P21) - Full data: P0=133.208±12.763/P7=102.294±73.180/P14=56.182±4.557/P21=52.228±3.077/P45=42.390±1.970/P180=34.883±4.130
VPM = 0.52494*(10**5) # 52.494 +/- 5.082 cells/mmˆ3 - Meyer, 2013 - average accross all VPM
# VPM = 0.83100*(10**5) # 83.100 +/- 7.900 cells/mmˆ3 - Sargeant, 2011 - Preffer to trust Meyer data on this case, because he quantified RTN and POm too
POm = 0.41477*(10**5) # 41.477 +/- 3.612 cells/mmˆ3 - Meyer, 2013

# Thalamic inhibition
RTN = 0.49680*(10**5) # 49.680 +/- 1.097 cells/mmˆ3 - Meyer, 2013
'''

# BLUE BRAIN DATA - BBP(https://bbp.epfl.ch/nexus/cell-atlas/)
VL  = 67711.5
VM  = 68816
VPL = 60916.1
VPM = 76151.1
POm = 62144.8
RTN = 69417.7

# Density data
density[('thal','ALL')] = [ int(VL),   # VL  - Estimated to be equal VPM 
                            int(VM),   # VM  - Estimated to be equal VPM 
                            int(VPL),  # VPL - Estimated to be equal VPM 
                            int(VPM),  # VPM
                            int(POm),  # POm
                            int(RTN)]  # RTN

# see:  Thal:   https://docs.google.com/spreadsheets/d/1Rj1y3CtjVqjJDDDAL6M6lzGS6aR5kS5MGQdBnonV9UQ/edit#gid=2005388318
#       A1:     https://docs.google.com/spreadsheets/d/1rXU6ujzg6TBG59XEFuyE1HTJ6VWM-Jr9XIjMMOxvU1g/edit#gid=460197992



# ------------------------------------------------------------------------------------------------------------------
# 2) Percentage of Excitatory Cells [from Lefort09 (mouse S1)]
# Avg for L2/3, L5A, L5B, L6 from fig 2D 
# overall 85:15 ratio consistent with Markram 2015 (87% +- 1% and 13% +- 1%) -->> Again is this percentage or ratio? 
# This is taken from M1 model cellDensity.py & modified 
# -------------------------------------------------------------------------------------------------------------------
# Ratio of neurons in the population
'''
# LITERATURE DATA 
sTC = [
        0.94,   # VL        # Jager, 2021 // quoting "(Butler, 2008; Evangelio et al., 2018; Seabrook et al., 2013b)"
        0.94,   # VM        # Jager, 2021 // quoting "(Butler, 2008; Evangelio et al., 2018; Seabrook et al., 2013b)"
        1.0,    # VPL       # Łuczyńska, 2003 // Barbaresi, 1986
        1.0,    # VPM       # Łuczyńska, 2003 // Barbaresi, 1986
        0.94,   # POm       # Jager, 2021 // quoting "(Butler, 2008; Evangelio et al., 2018; Seabrook et al., 2013b)"
        0.0     # RTN
        ]
sTI = [
        0.06,   # VL        # Jager, 2021 // quoting "(Butler, 2008; Evangelio et al., 2018; Seabrook et al., 2013b)"
        0.06,   # VM        # Jager, 2021 // quoting "(Butler, 2008; Evangelio et al., 2018; Seabrook et al., 2013b)"
        0.0,    # VPL       # Łuczyńska, 2003 // Barbaresi, 1986
        0.0,    # VPM       # Łuczyńska, 2003 // Barbaresi, 1986
        0.06,   # POm       # Jager, 2021 // quoting "(Butler, 2008; Evangelio et al., 2018; Seabrook et al., 2013b)"
        0.0     # RTN
        ]
sRE = [
        0.0,    # VL
        0.0,    # VM
        0.0,    # VPL
        0.0,    # VPM
        0.0,    # POm
        1.0     # RTN
        ]
'''
# BLUE BRAIN DATA - BBP(https://bbp.epfl.ch/nexus/cell-atlas/)
sTC = [
        0.930,
        0.941,
        0.977,
        1.000,
        1.000,
        0.000
        ]
sTI = [
        0.070,
        0.059,
        0.023,
        0.000,
        0.000,
        0.000
        ]
sRE = [
        0.000,
        0.000,
        0.000,
        0.000,
        0.000,
        1.000
        ]

# percentE = {}
# percentE['EIratio'] = [ VL_ratio[0] ,
#                         VPL_ratio[0],
#                         VPM_ratio[0],
#                         POm_ratio[0],
#                         RTN_ratio[0]] # IMPROVE - needs references

# density[('thal','E')] = [round((density['nrn_density'][i] * percentE['EIratio'][i])) for i in range(len(density['nrn_density']))] # keep in mind this is number of excitatory cells / (mm^3)
# density[('thal','I')] = [round((density['nrn_density'][i] * (1-percentE['EIratio'][i]))) for i in range(len(density['nrn_density']))] 

# density[('thal','E')] = [round(density['nrn_density'][i]) * (percentE['EIratio'][i]) for i in range(len(density['nrn_density']))] # keep in mind this is number of excitatory cells / (mm^3)
# density[('thal','I')] = [round(density['nrn_density'][i]) * (1-percentE['EIratio'][i]) for i in range(len(density['nrn_density']))] 

density[('thal','sTC')] =    [int((density[('thal','ALL')][i])*(sTC[i])) for i in range(len(sTC))] 
density[('thal','sTI')] =    [int((density[('thal','ALL')][i])*(sTI[i])) for i in range(len(sTI))]
density[('thal','sRE')] =    [int((density[('thal','ALL')][i])*(sRE[i])) for i in range(len(sRE))]






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

