"""
cfg.py 

Simulation configuration for S1 model (using NetPyNE)
This file has sim configs as well as specification for parameterized values in netParams.py 

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import pickle
import os

cfg = specs.SimConfig()  

#------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Run parameters
#------------------------------------------------------------------------------
cfg.duration = 1.0*1e4 ## Duration of the sim, in ms  
cfg.dt = 0.025
cfg.seeds = {'conn': 4321, 'stim': 4321, 'loc': 4321} 
cfg.hParams = {'celsius': 34, 'v_init': -65}  
cfg.verbose = False
cfg.createNEURONObj = True
cfg.createPyStruct = True  
cfg.cvode_active = False
cfg.cvode_atol = 1e-6
cfg.cache_efficient = True
cfg.printRunTime = 0.1

cfg.includeParamsLabel = False
cfg.printPopAvgRates = True

cfg.checkErrors = False

#------------------------------------------------------------------------------
# Cells
#------------------------------------------------------------------------------
cfg.rootFolder = os.getcwd()

cfg.importCellMod = 'pkl' # or 'BBPtemplate'
cfg.celldiversity = True 
cfg.poptypeNumber = 61 # max 55 + 6
cfg.celltypeNumber = 213 # max 207 + 6
#------------------------------------------------------------------------------  
# S1 Cells
# Load 55 Morphological Names and Cell pop numbers -> L1:6 L23:10 L4:12 L5:13 L6:14
# Load 207 Morpho-electrical Names used to import the cells from 'cell_data/' -> L1:14 L23:43 L4:46 L5:52 L6:52
# Create [Morphological,Electrical] = number of cell metype in the sub-pop
with open('../info/anatomy/S1-cells-distributions-Mouse.txt') as mtype_file:
	mtype_content = mtype_file.read()       

cfg.popNumber = {}
cfg.cellNumber = {} 
cfg.popLabel = {} 
popParam = []
cellParam = []
cfg.meParamLabels = {} 
for line in mtype_content.split('\n')[:-1]:
	metype, mtype, etype, n, m = line.split()
	cfg.cellNumber[metype] = int(n)
	cfg.popLabel[metype] = mtype
	cfg.popNumber[mtype] = int(m)

	if mtype not in popParam:
		popParam.append(mtype)
	cellParam.append(metype)

cfg.S1pops = popParam[0:55]
cfg.S1cells = cellParam[0:207]

#------------------------------------------------------------------------------  
# TO DEBUG - Create only one Cell per MEtype in S1 cells
cfg.oneCellperMEtypeS1 = True 
if cfg.oneCellperMEtypeS1:
	cfg.popNumber = {}
	cfg.cellNumber = {} 
	for mtype in cfg.S1pops:
		cfg.popNumber[mtype] = 0

	for line in mtype_content.split('\n')[:-1]:
		metype, mtype, etype, n, m = line.split()
		if int(n) < 5:
			cfg.cellNumber[metype] = int(n)
			cfg.popNumber[mtype] = cfg.popNumber[mtype] + int(n)
		else:
			cfg.cellNumber[metype] = 5
			cfg.popNumber[mtype] = cfg.popNumber[mtype] + 5

#------------------------------------------------------------------------------  
# Thalamic Cells

cfg.thalamicpops = ['ss_RTN_o', 'ss_RTN_m', 'ss_RTN_i', 'VPL_sTC', 'VPM_sTC', 'POm_sTC_s1']

cfg.cellNumber['ss_RTN_o'] = 382
cfg.cellNumber['ss_RTN_m'] = 382
cfg.cellNumber['ss_RTN_i'] = 765
cfg.cellNumber['VPL_sTC'] = 656
cfg.cellNumber['VPM_sTC'] = 839
cfg.cellNumber['POm_sTC_s1'] = 685

for mtype in cfg.thalamicpops: # No diversity for while
	metype = mtype
	popParam.append(mtype)
	cfg.popLabel[metype] = mtype
	cellParam.append(metype)

	cfg.popNumber[mtype] = cfg.cellNumber[metype]

#------------------------------------------------------------------------------  

cfg.popParamLabels = popParam[0:cfg.poptypeNumber] # to debug
cfg.cellParamLabels = cellParam[0:cfg.celltypeNumber] # to debug

#------------------------------------------------------------------------------  
# TO DEBUG - Create only one Cell per MEtype (~1000 S1 cells + 6 Th cells)
cfg.oneCellperMEtype = 0 
if cfg.oneCellperMEtype:
	cfg.popNumber = {}
	cfg.cellNumber = {} 
	for mtype in cfg.popParamLabels:
		cfg.popNumber[mtype] = 0

	for line in mtype_content.split('\n')[:-1]:
		metype, mtype, etype, n, m = line.split()
		if int(n) < 5:
			cfg.cellNumber[metype] = int(n)
			cfg.popNumber[mtype] = cfg.popNumber[mtype] + int(n)
		else:
			cfg.cellNumber[metype] = 5
			cfg.popNumber[mtype] = cfg.popNumber[mtype] + 5

	for mtype in cfg.thalamicpops:
		cfg.cellNumber[mtype] = 1
		cfg.popNumber[mtype] = cfg.cellNumber[mtype]

#--------------------------------------------------------------------------
# Recording 
#------------------------------------------------------------------------------

cfg.allpops = cfg.popParamLabels
cfg.cellsrec = 2
if cfg.cellsrec == 0:  cfg.recordCells = cfg.allpops # record all cells
elif cfg.cellsrec == 1: cfg.recordCells = [(pop,0) for pop in cfg.allpops] # record one cell of each pop
elif cfg.cellsrec == 2: # record one cell of each cellMEtype (cfg.celldiversity = True)
	cfg.recordCells = []
	cellNumberLabel = 0 
	for metype in cfg.cellParamLabels:
		if metype in cfg.thalamicpops:
			if cfg.cellNumber[metype] < 5:
				for numberME in range(cfg.cellNumber[metype]):
					cfg.recordCells.append((cfg.popLabel[metype],cellNumberLabel+numberME))
			else:
				for numberME in range(10): #5
					cfg.recordCells.append((cfg.popLabel[metype],cellNumberLabel+numberME))
			cellNumberLabel = cellNumberLabel + cfg.cellNumber[metype]
			if cellNumberLabel == cfg.popNumber[cfg.popLabel[metype]]:
				cellNumberLabel = 0 

cfg.recordTraces = {'V_soma': {'sec':'soma', 'loc':0.5, 'var':'v'}}  ## Dict with traces to record
cfg.recordStim = False			
cfg.recordTime = False  		
cfg.recordStep = 0.1            

#------------------------------------------------------------------------------
# Saving
#------------------------------------------------------------------------------

cfg.simLabel = 'v1_batch0'
cfg.saveFolder = '../data/'+cfg.simLabel
# cfg.filename =                	## Set file output name
cfg.savePickle = False         	## Save pkl file
cfg.saveJson = True	           	## Save json file
cfg.saveDataInclude = ['simConfig'] ## 'simData' , 'simConfig', 'netParams'
cfg.backupCfgFile = None 		##  
cfg.gatherOnlySimData = False	##  
cfg.saveCellSecs = False			
cfg.saveCellConns = False	

#------------------------------------------------------------------------------
# Analysis and plotting 
#------------------------------------------------------------------------------
cfg.analysis['plotRaster'] = {'include': cfg.allpops, 'saveFig': True, 'showFig': False, 'orderInverse': True, 'timeRange': [0,cfg.duration], 'figSize': (36,18), 'labels': 'legend', 'popRates': True, 'fontSize':12, 'lw': 1, 'markerSize':2, 'marker': '.', 'dpi': 300} 

cfg.analysis['plotTraces'] = {'include': cfg.recordCells, 'oneFigPer': 'cell', 'overlay': True, 'timeRange': [0,cfg.duration], 'ylim': [-100,50], 'saveFig': True, 'showFig': False, 'figSize':(12,4)}

# cfg.analysis['plot2Dfiring']={'saveFig': True, 'figSize': (24,24), 'fontSize':16}

# cfg.analysis['plotConn'] = {'includePre': cfg.allpops, 'includePost': cfg.allpops, 'feature': 'convergence', 'groupBy': 'pop', 'figSize': (24,24), 'saveFig': True, 'orderBy': 'gid', 'graphType': 'matrix', 'fontSize': 18}

# cfg.analysis['plot2Dnet']   = {'include': cfg.allpops, 'saveFig': True, 'showConns': False, 'figSize': (24,24), 'fontSize':16}   # Plot 2D net cells and connections

# cfg.analysis['plotShape'] = {'includePre': cfg.recordCells, 'includePost': cfg.recordCells, 'showFig': False, 'includeAxon': False, 
                            # 'showSyns': False, 'saveFig': True, 'dist': 0.55, 'cvar': 'voltage', 'figSize': (24,12), 'dpi': 600}

#------------------------------------------------------------------------------
# Network 
#------------------------------------------------------------------------------

cfg.scale = 1.0 # reduce size
cfg.sizeY = 1378.8
cfg.sizeX = 300.0 # r = 150 um 
cfg.sizeZ = 300.0
cfg.scaleDensity = 1.0 # Number of cells = 7859

#------------------------------------------------------------------------------
# Spontaneous synapses + background - data from Rat
#------------------------------------------------------------------------------
cfg.addStimSynS1 = 0
cfg.rateStimE = 6.0
cfg.rateStimI = 9.0
#------------------------------------------------------------------------------
# Connectivity2
#------------------------------------------------------------------------------
##S1
cfg.addConn = 0

cfg.synWeightFractionEE = [1.0, 1.0] # E -> E AMPA to NMDA ratio
cfg.synWeightFractionEI = [1.0, 1.0] # E -> I AMPA to NMDA ratio
cfg.synWeightFractionII = [1.0, 1.0]  # I -> I GABAA to GABAB ratio
cfg.synWeightFractionIE = [1.0, 1.0]  # I -> E GABAA to GABAB ratio
cfg.EEGain = 1.0
cfg.EIGain = 1.0
cfg.IIGain = 1.0
cfg.IEGain = 1.0

##Th
cfg.connectTh = True
cfg.connect_RTN_RTN     = True
cfg.connect_TC_RTN      = True
cfg.connect_RTN_TC      = True

# parameters tuned in (simDate = '2021_04_16' / simCode = 'jv019' - 'stabilizing the Firing rates of the model')
cfg.yConnFactor             = 10 # y-tolerance form connection distance based on the x and z-plane radial tolerances (1=100%; 2=50%; 5=20%; 10=10%)
cfg.connProb_RTN_RTN        = 1.0 #None 
cfg.connWeight_RTN_RTN      = 100.0*2.0 # optimized to increase synchrony in (simDate = '2021_04_30' / simCode = 't_allpops_012') - old value: 0.5
cfg.connProb_TC_RTN         = 0.75 #None
cfg.connWeight_TC_RTN       = 100.0*1.5 #0.5
cfg.connProb_RTN_TC         = 0.75 #None
cfg.connWeight_RTN_TC       = 100.0*0.25 # optimized to increase synchrony in (simDate = '2021_04_30' / simCode = 't_allpops_013') - old value: 0.83

cfg.divergenceHO = 10
cfg.connLenghtConst = 200

## S1-Th
cfg.connect_TC_CTX      = False
cfg.connect_CTX_TC      = False


#------------------------------------------------------------------------------
# Current inputs 
#------------------------------------------------------------------------------
cfg.addIClamp = 1
 
cfg.IClamp = []
cfg.IClampnumber = 0

cfg.thalamocorticalconnections =  ['VPL_sTC', 'VPM_sTC', 'POm_sTC_s1'] #'L5_TTPC2', 'L6_TPC_L4'

for popName in cfg.thalamocorticalconnections:
    cfg.IClamp.append({'pop': popName, 'sec': 'soma', 'loc': 0.5, 'start': 0, 'dur': 25, 'amp': 2.0}) #pA
    cfg.IClampnumber=cfg.IClampnumber+1

#------------------------------------------------------------------------------
# NetStim inputs 
#------------------------------------------------------------------------------
## Attempt to add Background Noise inputs 
cfg.addNetStim = 0
cfg.weightLong = {'S1': 0.5, 'S2': 0.5} 
