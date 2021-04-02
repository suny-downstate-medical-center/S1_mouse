
"""
netParams.py

High-level specifications for S1 network model using NetPyNE

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import pickle, json
import os

netParams = specs.NetParams()   # object of class NetParams to store the network parameters


try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = cfg.scale # Scale factor for number of cells
netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume
   
# Layer	     height	  from	  to
# L1         0.089      0.000	0.089
# L2         0.070      0.089	0.159
# L3         0.128      0.159	0.286
# L4         0.134      0.286	0.421
# L5         0.263      0.421	0.684
# L6         0.316      0.684	1.000			 
# L23        0.198      0.089	0.286
# All     1378.8 um

cellModels = ['HH_full']
Epops = ['L23_PC', 'L4_PC', 'L4_SS', 'L4_SP', 
             'L5_TTPC1', 'L5_TTPC2', 'L5_STPC', 'L5_UTPC',
             'L6_TPC_L1', 'L6_TPC_L4', 'L6_BPC', 'L6_IPC', 'L6_UTPC']
Ipops = []
for popName in cfg.popParamLabels:
    if popName not in Epops:
        Ipops.append(popName)

layer = {'1':[0.0, 0.089], '2': [0.089,0.159], '3': [0.159,0.286], '23': [0.089,0.286], '4':[0.286,0.421], '5': [0.421,0.684], '6': [0.684,1.0], 
'longS1': [2.2,2.3], 'longS2': [2.3,2.4]}  # normalized layer boundaries

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.defaultThreshold = -10.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 0.1 # default conn delay (ms)(M1: 2.0 ms)
netParams.propVelocity = 300.0 #  300 μm/ms (Stuart et al., 1997)(M1: 500.0um/ms)

#------------------------------------------------------------------------------
# Cell parameters  # L1 70  L23 215  L4 230 L5 260  L6 260  = 1035
#------------------------------------------------------------------------------
folder = os.listdir('%s/cell_data/' % (cfg.rootFolder))
folder = sorted([d for d in folder if os.path.isdir('%s/cell_data/%s' % (cfg.rootFolder, d))])
folder = folder[0:5*int(cfg.celltypeNumber)] ## partial load to debug

## Load cell rules using BBP template
if cfg.importCellMod == 'BBPtemplate':

    def loadTemplateName(cellnumber):     
        outFolder = cfg.rootFolder+'/cell_data/'+folder[cellnumber]
        try:
            f = open(outFolder+'/template.hoc', 'r')
            for line in f.readlines():
                if 'begintemplate' in line:
                    return str(line)[14:-1]     
        except:
            print('Cannot read cell template from %s' % (outFolder))
            return False

    cellName = {}
    cellType = {}
    cellnumber = 0
    loadCellParams = folder
    for ruleLabel in loadCellParams:
        cellName[cellnumber] = ruleLabel
        cellTemplateName = loadTemplateName(cellnumber)
        # print(cellName[cellnumber], cellTemplateName)
        if cellTemplateName:
            cellRule = netParams.importCellParams(label=cellName[cellnumber], somaAtOrigin=False,
                conds={'cellType': cellName[cellnumber], 'cellModel': 'HH_full'},
                fileName='cellwrapper.py',
                cellName='loadCell',
                cellInstance = True,
                cellArgs={'cellName': cellName[cellnumber], 'cellTemplateName': cellTemplateName})
            netParams.renameCellParamsSec(label=cellName[cellnumber], oldSec='soma_0', newSec='soma')
            os.chdir(cfg.rootFolder)
        cellnumber = cellnumber + 1

## Load cell rules previously saved using netpyne format before popParams
if cfg.importCellMod == 'pkl_before':
    loadCellParams = folder
    cellName = {}
    cellnumber = 0
    for ruleLabel in loadCellParams:
        cellName[cellnumber] = ruleLabel
        netParams.loadCellParamsRule(label = ruleLabel, fileName = 'cell_data/' + ruleLabel + '/' + ruleLabel + '_cellParams.pkl')    
        netParams.renameCellParamsSec(label=cellName[cellnumber], oldSec='soma_0', newSec='soma')
        cellnumber = cellnumber + 1

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------
for popName in cfg.popParamLabels:
	layernumber = popName[1:2]
	if layernumber == '2':
		netParams.popParams[popName] = {'cellType': popName, 'cellModel': 'HH_full', 'ynormRange': layer['23'], 'numCells': int(cfg.scaleDensity*cfg.popNumber[popName]+0.5), 'diversity': cfg.celldiversity}
	else:
		netParams.popParams[popName] = {'cellType': popName, 'cellModel': 'HH_full', 'ynormRange': layer[layernumber], 'numCells': int(cfg.scaleDensity*cfg.popNumber[popName]+0.5), 'diversity': cfg.celldiversity}

## Cell property rules
# cfg.reducedtest = True
cellnumber = 0    
if cfg.celldiversity:
    for cellName in cfg.cellParamLabels:
        
        if cfg.cellNumber[cellName] < 5:
            morphoNumbers = cfg.cellNumber[cellName]
        else:
            morphoNumbers = 5
        
        popName = cfg.popLabel[cellName]
        cellFraction = 1.0*cfg.cellNumber[cellName]/(morphoNumbers*cfg.popNumber[popName])
        
        if cfg.verbose:
            print(popName,cellName,cfg.cellNumber[cellName],cfg.popNumber[popName],morphoNumbers*cellFraction)
            print('diversityFraction =',morphoNumbers*cellFraction)

        for morphoNumber in range(morphoNumbers):
            cellMe = cellName + '_' + str(morphoNumber+1)
            ## Load cell rules previously saved using netpyne format
            if cfg.importCellMod == 'pkl_after':
                netParams.loadCellParamsRule(label = cellMe, fileName = 'cell_data/' + cellMe + '/' + cellMe + '_cellParams.pkl')    
                netParams.renameCellParamsSec(label = cellMe, oldSec = 'soma_0', newSec = 'soma')

            cellRule = {'conds': {'cellType': popName}, 'diversityFraction': cellFraction, 'secs': {}}  # cell rule dict
            cellRule['secs'] = netParams.cellParams[cellMe]['secs']     
            cellRule['conds'] = netParams.cellParams[cellMe]['conds']    
            cellRule['conds']['cellType'] = popName
            cellRule['globals'] = netParams.cellParams[cellMe]['globals']       
            cellRule['secLists'] = netParams.cellParams[cellMe]['secLists']                 
            cellRule['secLists']['all'][0] = 'soma' # replace 'soma_0'
            cellRule['secLists']['somatic'][0]  = 'soma' # replace 'soma_0'
                                  
            cellRule['secLists']['spiny'] = {}
            cellRule['secLists']['spinyEE'] = {}

            nonSpiny = ['axon_0', 'axon_1']
            cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['all'] if sec not in nonSpiny]
            nonSpinyEE = ['axon_0', 'axon_1', 'soma']
            cellRule['secLists']['spinyEE'] = [sec for sec in cellRule['secLists']['all'] if sec not in nonSpinyEE]

            # if cfg.reducedtest:
            #     cellRule['secs'] = {}
            #     cellRule['secs']['soma'] = netParams.cellParams[cellMe]['secs']['soma']   
                # cellRule['secs']['dend_0'] = netParams.cellParams[cellMe]['secs']['dend_0']   
                # cellRule['secs']['dend_1'] = netParams.cellParams[cellMe]['secs']['dend_1']    
                # cellRule['secs']['axon_0']  = netParams.cellParams[cellMe]['secs']['axon_0']   
                # cellRule['secs']['axon_1'] = netParams.cellParams[cellMe]['secs']['axon_1']      
                # if 'apic_1' in cellRule['secLists']['apical']:
                #     cellRule['secs']['apic_0']  = netParams.cellParams[cellMe]['secs']['apic_0']
                #     cellRule['secs']['apic_1']  = netParams.cellParams[cellMe]['secs']['apic_1']

            netParams.cellParams[cellMe] = cellRule   # add dict to list of cell params   

            cellnumber=cellnumber+1  	
            
#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
### mods from M1 detailed
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 1.74, 'e': 0}
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 0.29, 'tau2NMDA': 43, 'e': 0}
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 8.3, 'e': -80}
netParams.synMechParams['GABAB'] = {'mod':'MyExp2SynBB', 'tau1': 3.5, 'tau2': 260.9, 'e': -93} 

ESynMech = ['AMPA', 'NMDA']
ISynMech = ['GABAA', 'GABAB']

#------------------------------------------------------------------------------
# Local connectivity parameters
#------------------------------------------------------------------------------
## load data from conn pre-processing file
with open('conn/conn.pkl', 'rb') as fileObj: connData = pickle.load(fileObj)

pmatfull = connData['pmat']
connNumber = connData['connNumber']

lmat = connData['lmat']
a0mat = connData['a0mat']
d0 = connData['d0']
dfinal = connData['dfinal']
pmat = {}
pmat[12.5] = connData['pmat12um']
pmat[25] = connData['pmat25um']
pmat[50] = connData['pmat50um']
pmat[75] = connData['pmat75um']
pmat[100] = connData['pmat100um']
pmat[125] = connData['pmat125um']
pmat[150] = connData['pmat150um']
pmat[175] = connData['pmat175um']
pmat[200] = connData['pmat200um']
pmat[225] = connData['pmat225um']
pmat[250] = connData['pmat250um']
pmat[275] = connData['pmat275um']
pmat[300] = connData['pmat300um']
pmat[325] = connData['pmat325um']
pmat[350] = connData['pmat350um']
pmat[375] = connData['pmat375um']
synperconnNumber = connData['synperconnNumber']
synperconnNumberStd = connData['synperconnNumberStd']
decay = connData['decay']
decayStd  = connData['decayStd']
gsyn = connData['gsyn']
gsynStd = connData['gsynStd']
connDataSource = connData['connDataSource']
#------------------------------------------------------------------------------
if cfg.addConn:      
# I -> I
    for pre in Ipops:
        for post in Ipops:
            if float(connNumber[pre][post]) > 0:        

                if int(float(d0[pre][post])) < 25:    #d0==12.5 -> single exponential fit
                    linear = 0
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D))))' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post])                     
                elif int(float(d0[pre][post])) == 25:    #d0==25 -> exponential fit when dist_2D>25, else prob[0um:25um] = pmat[12.5]
                    linear = float(pmat[12.5][pre][post])
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)
                else:    #d0>25 -> exponential fit when dist_2D>d0, else prob[0um:d0] = linear interpolation [25:d0]
                    d01 = int(float(d0[pre][post]))
                    y1 = float(pmat[25][pre][post])
                    y2 = float(pmat[d01][pre][post])
                    x1 = 25
                    x2 = d01                   
                    angular = (y2 - y1)/(x2 - x1)
                    linear = y2 - x2*angular
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)

                netParams.connParams['II_'+pre+'_'+post] = { 
                    'preConds': {'pop': pre}, 
                    'postConds': {'pop': post},
                    'synMech': ISynMech,
                    'probability': prob,
                    'weight': gsyn[pre][post] * cfg.IIGain, 
                    'synMechWeightFactor': cfg.synWeightFractionII,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': int(synperconnNumber[pre][post]+0.5),
                    'sec': 'spiny'}       

## I -> E
    for pre in Ipops:
        for post in Epops:
            if float(connNumber[pre][post]) > 0:        

                if int(float(d0[pre][post])) < 25:    #d0==12.5 -> single exponential fit
                    linear = 0
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D))))' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post])                     
                elif int(float(d0[pre][post])) == 25:    #d0==25 -> exponential fit when dist_2D>25, else prob[0um:25um] = pmat[12.5]
                    linear = float(pmat[12.5][pre][post])
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)
                else:    #d0>25 -> exponential fit when dist_2D>d0, else prob[0um:d0] = linear interpolation [25:d0]
                    d01 = int(float(d0[pre][post]))
                    y1 = float(pmat[25][pre][post])
                    y2 = float(pmat[d01][pre][post])
                    x1 = 25
                    x2 = d01                   
                    angular = (y2 - y1)/(x2 - x1)
                    linear = y2 - x2*angular
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)

                netParams.connParams['IE_'+pre+'_'+post] = { 
                    'preConds': {'pop': pre}, 
                    'postConds': {'pop': post},
                    'synMech': ISynMech,
                    'probability': prob,
                    'weight': gsyn[pre][post] * cfg.IEGain, 
                    'synMechWeightFactor': cfg.synWeightFractionIE,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': int(synperconnNumber[pre][post]+0.5),
                    'sec': 'spiny'}     
#------------------------------------------------------------------------------   
## E -> E
    for pre in Epops:
        for post in Epops:
            if float(connNumber[pre][post]) > 0:        

                if int(float(d0[pre][post])) < 25:    #d0==12.5 -> single exponential fit
                    linear = 0
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D))))' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post])                     
                elif int(float(d0[pre][post])) == 25:    #d0==25 -> exponential fit when dist_2D>25, else prob[0um:25um] = pmat[12.5]
                    linear = float(pmat[12.5][pre][post])
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)
                else:    #d0>25 -> exponential fit when dist_2D>d0, else prob[0um:d0] = linear interpolation [25:d0]
                    d01 = int(float(d0[pre][post]))
                    y1 = float(pmat[25][pre][post])
                    y2 = float(pmat[d01][pre][post])
                    x1 = 25
                    x2 = d01                   
                    angular = (y2 - y1)/(x2 - x1)
                    linear = y2 - x2*angular
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)

                netParams.connParams['EE_'+pre+'_'+post] = { 
                    'preConds': {'pop': pre}, 
                    'postConds': {'pop': post},
                    'synMech': ESynMech,
                    'probability': prob, 
                    'weight': gsyn[pre][post] * cfg.EEGain, 
                    'synMechWeightFactor': cfg.synWeightFractionEE,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': int(synperconnNumber[pre][post]+0.5),
                    'sec': 'spinyEE'}    

# ## E -> I
    for pre in Epops:
        for post in Ipops:
            if float(connNumber[pre][post]) > 0:        

                if int(float(d0[pre][post])) < 25:    #d0==12.5 -> single exponential fit
                    linear = 0
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D))))' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post])                     
                elif int(float(d0[pre][post])) == 25:    #d0==25 -> exponential fit when dist_2D>25, else prob[0um:25um] = pmat[12.5]
                    linear = float(pmat[12.5][pre][post])
                    angular = 0
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)
                else:    #d0>25 -> exponential fit when dist_2D>d0, else prob[0um:d0] = linear interpolation [25:d0]
                    d01 = int(float(d0[pre][post]))
                    y1 = float(pmat[25][pre][post])
                    y2 = float(pmat[d01][pre][post])
                    x1 = 25
                    x2 = d01                   
                    angular = (y2 - y1)/(x2 - x1)
                    linear = y2 - x2*angular
                    prob = '%s * exp(-dist_2D/%s) * (1.0/(1+exp(-2000*(%s-dist_2D)))) if dist_2D > %s else %f * dist_2D + %f' % (a0mat[pre][post],lmat[pre][post],dfinal[pre][post],d0[pre][post],angular,linear)

                netParams.connParams['EI_'+pre+'_'+post] = { 
                    'preConds': {'pop': pre}, 
                    'postConds': {'pop': post},
                    'synMech': ESynMech,
                    'probability': prob, 
                    'weight': gsyn[pre][post] * cfg.EIGain, 
                    'synMechWeightFactor': cfg.synWeightFractionEI,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'synsPerConn': int(synperconnNumber[pre][post]+0.5),
                    'sec': 'spiny'}    
#------------------------------------------------------------------------------    
# Current inputs (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:
     for j in range(cfg.IClampnumber):
        key ='IClamp'
        params = getattr(cfg, key, None)
        key ='IClamp'+str(j+1)
        params = params[j]
        [pop,sec,loc,start,dur,amp] = [params[s] for s in ['pop','sec','loc','start','dur','amp']]

        # add stim source
        netParams.stimSourceParams[key] = {'type': 'IClamp', 'delay': start, 'dur': dur, 'amp': amp}
        
        # connect stim source to target
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop},
            'sec': sec, 
            'loc': loc}

#------------------------------------------------------------------------------
# NetStim inputs to simulate quantal synapses
#------------------------------------------------------------------------------
if cfg.addQuantalSyn:      
    for post in Ipops + Epops:
        for pre in Ipops:
            if float(connNumber[pre][post]) > 0:
                synTotal = float(connNumber[pre][post])*int(synperconnNumber[pre][post]+0.5)            
                synperNeuron = synTotal/cfg.popNumber[post]
                ratespontaneous = 0.5
                synperNeuron = synperNeuron*ratespontaneous
                netParams.stimSourceParams['quantalS_' + pre + '->' + post] = {'type': 'NetStim', 'rate': synperNeuron, 'noise': 1.0}

        for pre in Epops:
            if float(connNumber[pre][post]) > 0:
                synTotal = float(connNumber[pre][post])*int(synperconnNumber[pre][post]+0.5)
                synperNeuron = synTotal/cfg.popNumber[post]
                ratespontaneous = 0.1
                synperNeuron = synperNeuron*ratespontaneous
                netParams.stimSourceParams['quantalS_' + pre + '->' + post] = {'type': 'NetStim', 'rate': synperNeuron, 'noise': 1.0}
    #------------------------------------------------------------------------------
    for post in Ipops:
        for pre in Epops:
            if float(connNumber[pre][post]) > 0:
                netParams.stimTargetParams['quantalT_' + pre + '->' + post] = {
                    'source': 'quantalS_' + pre + '->' + post, 
                    'conds': {'cellType': post}, 
                    'ynorm':[0,1], 
                    'sec': 'soma', 
                    'loc': 0.5, 
                    'synMechWeightFactor': [1.0],
                    'weight': 0.001 * gsyn[pre][post], 
                    'delay': 0.5, 
                    'synMech': 'AMPA'}

    for post in Epops:
        for pre in Epops:
            if float(connNumber[pre][post]) > 0:
                netParams.stimTargetParams['quantalT_' + pre + '->' + post] = {
                    'source': 'quantalS_' + pre + '->' + post, 
                    'conds': {'cellType': post}, 
                    'ynorm':[0,1], 
                    'sec': 'soma', 
                    'loc': 0.5, 
                    'synMechWeightFactor': [1.0],
                    'weight': 0.001 * gsyn[pre][post], 
                    'delay': 0.5, 
                    'synMech': 'AMPA'}

    for post in Ipops + Epops:
        for pre in Ipops:
            if float(connNumber[pre][post]) > 0:
                netParams.stimTargetParams['quantalT_' + pre + '->' + post] = {
                    'source': 'quantalS_' + pre + '->' + post, 
                    'conds': {'cellType': post}, 
                    'ynorm':[0,1], 
                    'sec': 'soma', 
                    'loc': 0.5, 
                    'synMechWeightFactor': [1.0],
                    'weight': 0.001 * gsyn[pre][post], 
                    'delay': 0.5, 
                    'synMech': 'GABAA'}
                    
#------------------------------------------------------------------------------
# Description
#------------------------------------------------------------------------------
netParams.description = """ 
- Code based: M1 net, 6 layers, 7 cell types - v103
- v0 - insert cell diversity
- v1 - insert connection rules
- v2 - insert phys conn parameters
- v3 - ajust conn number
- v4 - talamic input and quantal synapses
"""
