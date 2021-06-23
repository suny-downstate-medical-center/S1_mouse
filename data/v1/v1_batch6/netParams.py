
"""
netParams.py

High-level specifications for S1 network model using NetPyNE

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import pickle, json
import os
import numpy as np

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
for popName in cfg.S1pops:
    if popName not in Epops:
        Ipops.append(popName)

layer = {'1':[0.0, 0.089], '2': [0.089,0.159], '3': [0.159,0.286], '23': [0.089,0.286], '4':[0.286,0.421], '5': [0.421,0.684], '6': [0.684,1.0], 
'longS1': [2.2,2.3], 'longS2': [2.3,2.4]}  # normalized layer boundaries

#Th pop
ymin={'ss_RTN_o': 1688, 'ss_RTN_m': 1766, 'ss_RTN_i': 1844, 'VPL_sTC': 2000, 'VPM_sTC': 2156, 'POm_sTC_s1': 2312}
ymax={'ss_RTN_o': 1766, 'ss_RTN_m': 1844, 'ss_RTN_i': 2000, 'VPL_sTC': 2156, 'VPM_sTC': 2312, 'POm_sTC_s1': 2624}

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.defaultThreshold = -10.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 0.1 # default conn delay (ms)(M1: 2.0 ms)
netParams.propVelocity = 300.0 #  300 μm/ms (Stuart et al., 1997)(M1: 500.0um/ms)
netParams.scaleConnWeight = 0.001 # weight conversion factor (from nS to uS)
netParams.scaleConnWeightNetStims = 0.001  # weight conversion factor (from nS to uS)

#------------------------------------------------------------------------------
# Cell parameters  # L1 70  L23 215  L4 230 L5 260  L6 260  = 1035
#------------------------------------------------------------------------------
folder = os.listdir('%s/cell_data/' % (cfg.rootFolder))
folder = sorted([d for d in folder if os.path.isdir('%s/cell_data/%s' % (cfg.rootFolder, d))])

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

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------
## S1
for popName in cfg.S1pops:
	layernumber = popName[1:2]
	if layernumber == '2':
		netParams.popParams[popName] = {'cellType': popName, 'cellModel': 'HH_full', 'ynormRange': layer['23'], 
                                        'numCells': int(np.ceil(cfg.scaleDensity*cfg.popNumber[popName])), 'diversity': True}
	else:
		netParams.popParams[popName] = {'cellType': popName, 'cellModel': 'HH_full', 'ynormRange': layer[layernumber], 
                                        'numCells': int(np.ceil(cfg.scaleDensity*cfg.popNumber[popName])), 'diversity': True}

## THALAMIC POPULATIONS (from prev model)
for popName in cfg.thalamicpops:
    if 'RTN' in popName: # inhibitory - RTN
        ThcellType = 'sRE_cell'
    else: # excitatory
        ThcellType = 'sTC_cell'    
    netParams.popParams[popName] = {'cellType': ThcellType, 'cellModel': 'HH_full', 'yRange': [ymin[popName], ymax[popName]],
                                        'numCells':  int(np.ceil(cfg.scaleDensity*cfg.popNumber[popName])), 'diversity': False}

## S1 cell property rules
cellnumber = 0    
for cellName in cfg.S1cells:
    
    if cfg.cellNumber[cellName] < 5:
        morphoNumbers = cfg.cellNumber[cellName]
    else:
        morphoNumbers = 5
    
    popName = cfg.popLabel[cellName]
    cellFraction = 1.0*cfg.cellNumber[cellName]/(morphoNumbers*cfg.popNumber[popName])
    
    for morphoNumber in range(morphoNumbers):
        cellMe = cellName + '_' + str(morphoNumber+1)
        ## Load cell rules previously saved using netpyne format
        if cfg.importCellMod == 'pkl':
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

        #-----------------------------------------------------------------------------------#
        cfg.reducedtest = False    
        if cfg.reducedtest:
            cellRule['secs'] = {}
            cellRule['secs']['soma'] = netParams.cellParams[cellMe]['secs']['soma']
            # cellRule['secs']['dend_0'] = netParams.cellParams[cellMe]['secs']['dend_0']
            # cellRule['secs']['axon_0']  = netParams.cellParams[cellMe]['secs']['axon_0']
            # cellRule['secs']['axon_1'] = netParams.cellParams[cellMe]['secs']['axon_1']
            
            # if 'apic_0' in cellRule['secLists']['apical']:
            #     cellRule['secs']['apic_0']  = netParams.cellParams[cellMe]['secs']['apic_0']
            #     cellRule['secLists']['spiny'] = ['soma','dend_0','apic_0']
            #     cellRule['secLists']['spinyEE'] = ['dend_0','apic_0']
            #     cellRule['secLists']['all'] = ['soma','dend_0','apic_0','axon_0', 'axon_1']
            #     cellRule['secLists']['apical'] = ['apic_0']
            #     cellRule['secLists']['basal'] = ['dend_0']
            # else:
            #     cellRule['secLists']['spiny'] = ['soma','dend_0']
            #     cellRule['secLists']['spinyEE'] = ['dend_0']
            #     cellRule['secLists']['all'] = ['soma','dend_0','axon_0', 'axon_1']
            #     cellRule['secLists']['basal'] = ['dend_0']    

            # only soma to test the net
            cellRule['secLists']['spiny'] = ['soma']
            cellRule['secLists']['spinyEE'] = ['soma']
            cellRule['secLists']['all'] = ['soma']
            cellRule['secLists']['basal'] = ['soma']    
        #-----------------------------------------------------------------------------------#
        netParams.cellParams[cellMe] = cellRule   # add dict to list of cell params   
        cellnumber=cellnumber+1        

## Th cell property rules
# JSON FILES FROM A1 WITH UPDATED DYNAMICS
#     # # --- VL - Exc --- #
netParams.loadCellParamsRule(label='sTC_cell', fileName='cells/sTC_jv_00.json')  # Load cellParams for each of the above cell subtype
netParams.cellParams['sTC_cell']['conds']={}

#     # --- RTN - Inh --- #
netParams.loadCellParamsRule(label='sRE_cell', fileName='cells/sRE_jv_00.json')  # Load cellParams for each of the above cell subtype
netParams.cellParams['sRE_cell']['conds']={}

#------------------------------------------------------------------------------
# Synaptic mechanism parameters  - mods from M1 detailed
#------------------------------------------------------------------------------
## S1
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 1.74, 'e': 0}
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 0.29, 'tau2NMDA': 43, 'e': 0}
netParams.synMechParams['GABAA6'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 6.44, 'e': -80}
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 8.3, 'e': -80}
netParams.synMechParams['GABAA10'] = {'mod':'MyExp2SynBB', 'tau1': 0.2, 'tau2': 10.4, 'e': -80}
netParams.synMechParams['GABAB'] = {'mod':'MyExp2SynBB', 'tau1': 3.5, 'tau2': 260.9, 'e': -93} 

ESynMech = ['AMPA', 'NMDA']
ISynMech = ['GABAA', 'GABAB']
ISynMech6 = ['GABAA6', 'GABAB']
ISynMech10 = ['GABAA10', 'GABAB']

## Th
netParams.synMechParams['NMDA_Th']             = {'mod': 'MyExp2SynNMDABB',    'tau1NMDA': 15, 'tau2NMDA': 150,                'e': 0}
netParams.synMechParams['AMPA_Th']             = {'mod': 'MyExp2SynBB',        'tau1': 0.05,   'tau2': 5.3, 'e': 0}
netParams.synMechParams['GABAB_Th']            = {'mod': 'MyExp2SynBB',        'tau1': 3.5,    'tau2': 260.9,                  'e': -93} 
netParams.synMechParams['GABAA_Th']            = {'mod': 'MyExp2SynBB',        'tau1': 0.07,   'tau2': 18.2,                   'e': -80}
netParams.synMechParams['GABAASlow_Th']        = {'mod': 'MyExp2SynBB',        'tau1': 2,      'tau2': 100,                    'e': -80}
netParams.synMechParams['GABAASlowSlow_Th']    = {'mod': 'MyExp2SynBB',        'tau1': 200,    'tau2': 400,                    'e': -80}

ESynMech_Th    = ['AMPA_Th', 'NMDA_Th']
SOMESynMech_Th = ['GABAASlow_Th','GABAB_Th']
SOMISynMech_Th = ['GABAASlow_Th']
PVSynMech_Th   = ['GABAA_Th']
NGFSynMech_Th  = ['GABAA_Th', 'GABAB_Th']


#------------------------------------------------------------------------------
# Th connectivity parameters
#------------------------------------------------------------------------------
if cfg.connectTh:

    ## load data from conn pre-processing file
    with open('conn/conn_Th.pkl', 'rb') as fileObj: connData = pickle.load(fileObj)
    pmat = connData['pmat']
    lmat = connData['lmat']
    wmat = connData['wmat']
    cmat = connData['cmat']
    
    pops_TC     = ['VPL_sTC','VPM_sTC', 'POm_sTC_s1']
    pops_RTN    = ['ss_RTN_o', 'ss_RTN_m', 'ss_RTN_i']
    pops_FO     = ['VPL_sTC','VPM_sTC']
    pops_HO     = ['POm_sTC_s1']

    # Intrathalamic 
    if cfg.connect_RTN_RTN:        
        for pre in pops_RTN:
            for post in pops_RTN:
                if pre in pmat and post in pmat[pre]:

                    pmat[pre][post]=cfg.connProb_RTN_RTN
                    wmat[pre][post]=cfg.connWeight_RTN_RTN

                    l = cfg.connLenghtConst
                    syn = PVSynMech_Th # only GABA A
                    synWeightFactor = [1.0]
                    netParams.connParams['thal_'+pre+'_'+post] = { 
                                    'preConds': {'pop': pre}, 
                                    'postConds': {'pop': post},
                                    'synMech': syn,
                                    'probability':' %f * exp(-dist_3D/%f)*(dist_2D<%f)*(dist_y<(%f/%f))' % (pmat[pre][post], l, cmat[pre][post], cmat[pre][post],cfg.yConnFactor),
                                    'weight': wmat[pre][post], 
                                    'synMechWeightFactor': synWeightFactor,
                                    'delay': 'defaultDelay+dist_3D/propVelocity',
                                    'synsPerConn': 10,
                                    'sec': 'soma'}

    if cfg.connect_TC_RTN:
        for pre in pops_TC:
            for post in pops_RTN:
                if pre in pmat and post in pmat[pre]:

                    pmat[pre][post]=cfg.connProb_TC_RTN
                    wmat[pre][post]=cfg.connWeight_TC_RTN

                    l = cfg.connLenghtConst
                    y_thresh    = cmat[pre][post]/5

                    syn = ['AMPA_Th'] # AMPA
                    synWeightFactor = [1.0]

                    if pre in pops_HO:
                        conn_method = 'divergence'
                        prob_rule = cfg.divergenceHO
                    else: # topographycal connectivity
                        conn_method = 'probability'
                        prob_rule = '%f * exp(-dist_2D/%f)*(dist_2D<%f)*(abs(((((pre_y-%f)*(%f-%f))/(%f-%f))+%f)-post_y)<%f)' % (pmat[pre][post], l, cmat[pre][post],ymin[pre],ymax[post],ymin[post],ymax[pre],ymin[pre],ymin[post],y_thresh)

                    netParams.connParams['thal_'+pre+'_'+post] = { 
                                'preConds': {'pop': pre}, 
                                'postConds': {'pop': post},
                                'synMech': syn,
                                conn_method:  prob_rule,
                                'weight': wmat[pre][post], 
                                'synMechWeightFactor': synWeightFactor,
                                'delay': 'defaultDelay+dist_3D/propVelocity',
                                'synsPerConn': 10,
                                'sec': 'soma'}

    if cfg.connect_RTN_TC:
        for pre in pops_RTN:
            for post in pops_TC:
                if pre in pmat and post in pmat[pre]:

                    pmat[pre][post]=cfg.connProb_RTN_TC
                    wmat[pre][post]=cfg.connWeight_RTN_TC

                    l = cfg.connLenghtConst
                    y_thresh    = cmat[pre][post]/5

                    syn = NGFSynMech_Th    # GABA A and GABA B
                    synWeightFactor = [0.6,0.4]
                            
                    if post in pops_HO:
                        conn_method = 'divergence'
                        prob_rule = cfg.divergenceHO
                    else: # topographycal connectivity
                        conn_method = 'probability'
                        prob_rule = '%f * exp(-dist_2D/%f)*(dist_2D<%f)*(abs(((((pre_y-%f)*(%f-%f))/(%f-%f))+%f)-post_y)<%f)' % (pmat[pre][post], l, cmat[pre][post],ymin[pre],ymax[post],ymin[post],ymax[pre],ymin[pre],ymin[post],y_thresh)

                    netParams.connParams['thal_'+pre+'_'+post] = { 
                                'preConds': {'pop': pre}, 
                                'postConds': {'pop': post},
                                'synMech': syn,
                                conn_method:  prob_rule,
                                'weight': wmat[pre][post], 
                                'synMechWeightFactor': synWeightFactor,
                                'delay': 'defaultDelay+dist_3D/propVelocity',
                                'synsPerConn': 10,
                                'sec': 'soma'}


## load data from S1 conn pre-processing file 
with open('conn/conn.pkl', 'rb') as fileObj: connData = pickle.load(fileObj)

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
pmat[200] = connData['pmat200um'] #max value for d0=200

synperconnNumber = connData['synperconnNumber']
connNumber = connData['connNumber']
decay = connData['decay']
gsyn = connData['gsyn']
use = connData['use']

# print(netParams.connParams)

#------------------------------------------------------------------------------
# S1 Local connectivity parameters 
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
                
                if decay[pre][post] > 10.0:
                    synMechType =  ISynMech10
                elif decay[pre][post] < 7.0:
                    synMechType =  ISynMech6
                else:
                    synMechType =  ISynMech

                netParams.connParams['II_'+pre+'_'+post] = { 
                    'preConds': {'pop': pre}, 
                    'postConds': {'pop': post},
                    'synMech': synMechType,
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

                if decay[pre][post] > 10.0:
                    synMechType =  ISynMech10
                elif decay[pre][post] < 7.0:
                    synMechType =  ISynMech6
                else:
                    synMechType =  ISynMech

                netParams.connParams['IE_'+pre+'_'+post] = { 
                    'preConds': {'pop': pre}, 
                    'postConds': {'pop': post},
                    'synMech': synMechType,
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
# NetStim inputs to simulate Spontaneous synapses + background - data from Rat
#------------------------------------------------------------------------------
SourcesNumber = 5 # for each post Mtype - sec distribution
synperNeuronStimI = connData['synperNeuronStimI']
synperNeuronStimE = connData['synperNeuronStimE']
GsynStimI = connData['GsynStimI']
GsynStimE = connData['GsynStimE']
   
if cfg.addStimSynS1:      
    for post in Ipops + Epops:

        synperNeuron = synperNeuronStimI[post]
        ratespontaneous = cfg.rateStimI
        for qSnum in range(SourcesNumber):
            ratesdifferentiation = (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (synperNeuron*ratespontaneous)/SourcesNumber
            netParams.stimSourceParams['StimSynS1_S_all_INH->' + post + '_' + str(qSnum)] = {'type': 'NetStim', 'rate': ratesdifferentiation, 'noise': 1.0}

        synperNeuron = synperNeuronStimE[post]
        ratespontaneous = cfg.rateStimE
        for qSnum in range(SourcesNumber):
            ratesdifferentiation = (0.8 + 0.4*qSnum/(SourcesNumber-1)) * (synperNeuron*ratespontaneous)/SourcesNumber
            netParams.stimSourceParams['StimSynS1_S_all_EXC->' + post + '_' + str(qSnum)] = {'type': 'NetStim', 'rate': ratesdifferentiation, 'noise': 1.0}

    #------------------------------------------------------------------------------
    for post in Epops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSynS1_T_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_EXC->' + post + '_' + str(qSnum), 
                'conds': {'cellType': post}, 
                'ynorm':[0,1], 
                'sec': 'spinyEE', 
                'loc': 0.5, 
                'synMechWeightFactor': [1.0],
                'weight': GsynStimE[post],
                'delay': 0.1, 
                'synMech': 'AMPA'}

    for post in Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSynS1_T_all_EXC->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_EXC->' + post + '_' + str(qSnum), 
                'conds': {'cellType': post}, 
                'ynorm':[0,1], 
                'sec': 'spiny', 
                'loc': 0.5, 
                'synMechWeightFactor': [1.0],
                'weight': GsynStimE[post],
                'delay': 0.1, 
                'synMech': 'AMPA'}

    for post in Epops+Ipops:
        for qSnum in range(SourcesNumber):
            netParams.stimTargetParams['StimSynS1_T_all_INH->' + post + '_' + str(qSnum)] = {
                'source': 'StimSynS1_S_all_INH->' + post + '_' + str(qSnum), 
                'conds': {'cellType': post}, 
                'ynorm':[0,1], 
                'sec': 'spiny', 
                'loc': 0.5, 
                'synMechWeightFactor': [1.0],
                'weight': GsynStimI[post],
                'delay': 0.1, 
                'synMech': 'GABAA'}

#------------------------------------------------------------------------------
# Description
#------------------------------------------------------------------------------
netParams.description = """ 
- Code based: M1 net, 6 layers, 7 cell types - v103
- v0Rat - insert cell diversity
- v1Rat - insert connection rules
- v2Rat - insert phys conn parameters
- v3Rat - ajust conn number
- v4Rat - StimSynS1_ synapses
- v0 - from v4 S1_Rat
- v1 - insert thalamic pops
"""
