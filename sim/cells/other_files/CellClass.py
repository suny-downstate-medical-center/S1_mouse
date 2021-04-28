#! /usr/bin/python3

'''
General HH Cell model
'''

from neuron import h

class HHCell():
	def __init__(self):
		# --- Initializing cell properties
		self.create_sections()
		self.build_topology()
		self.define_geometry()
		self.define_biophysics()
		self.set_position(None,None)

		# --- List of synapses
		self.synlist = []
		# --- List of network stimulus
		self.nclist=[]

	def create_sections(self):
		self.soma = h.Section(name='soma')
		self.dend = h.Section(name='dend')

	def build_topology(self):
		self.dend.connect(self.soma(1.0))

	#   Set Geometry of the Neurons
	def define_geometry(self):
	# def define_geometry(self, soma, dend):
		# --- Soma
		self.soma.L = self.soma.diam = 12.6157 # Makes a soma of 500 microns squared
		
		# --- Dendrite
		self.dend.L = 180 # microns
		self.dend.diam = 1 # microns

		# --- Setting the properties of the sections
		for sec in h.allsec():
			sec.Ra =  100   # Axial resistance in Ohm * cm
			sec.cm = 1      # Membrane capacitance in micro Farads / cm^2

	def define_biophysics(self):
	# def define_biophysics(self, soma, dend):
		 #   Insert a HH mechanism
		self.soma.insert('hh')
		self.soma.gnabar_hh = 0.12 # Sodium conductance in S/cm2
		self.soma.gkbar_hh = 0.036 # Potassium conductance in S/cm2
		self.soma.gl_hh = 0.0003 # Leak conductance in S/cm2
		self.soma.el_hh = -54.3 # Reversal potential in mV # Insert passive current in the dendrite
		# dend.g_pas = 0.001 # Passive conductance in S/cm2
		# dend.e_pas = -65 # Leak reversal potential mV

		self.dend.insert('pas')
		self.dend.nseg = 11
		self.dend.g_pas = 0.001
		self.dend.e_pas = -65

		self.soma(0.5).hh.gnabar = 0.13
		self.dend(0.5).pas.e = -65
	
	def set_position(self,x,y):
		self.x = x
		self.y = y

	def add_current_stim(self,inputDelay):
	# def add_current_stim(self,dend):
		self.stim = h.IClamp(self.dend(1.0))

		self.stim.amp    = 0.3 # input current in nA
		self.stim.delay  = inputDelay # turn on after this time in ms
		self.stim.dur    = 1

	def create_synapse(self,loc=0.5,tau=2,e=0):
		syn = h.ExpSyn(self.dend(loc)) # add excitatory synapse
		syn.e = e
		syn.tau = tau
		self.synlist.append(syn)

	def connect2pre(self,preCell,synid=0,delay=2,weight=1):
		nc = h.NetCon(preCell.soma(0.5)._ref_v, self.synlist[synid], sec=preCell.soma)
		nc.weight[0] = weight
		nc.delay = delay
		self.nclist.append(nc)

	def record_voltage(self,simDuration = 40):
	# def record_voltage(self,soma,dend):
		# Create 3 vector to store the values
		self.v_vec_soma  = h.Vector() # Membrane potential vector
		self.v_vec_dend  = h.Vector() # Membrane potential vector
		self.t_vec       = h.Vector() # Time stamp vector
		# Tells neuron where to record what
		self.v_vec_soma.record(self.soma(0.5)._ref_v)
		self.v_vec_dend.record(self.dend(0.5)._ref_v)
		self.t_vec.record(h._ref_t)

		# h.tstop = simDuration
		# h.run()

	def plot_voltage(self,cellId):
		from matplotlib import pyplot as plt
		# plt.figure(figsize=(8,4)) # Default figsize is (8,6)
		plt.plot(self.t_vec, self.v_vec_soma, 'b', label='soma')
		plt.plot(self.t_vec, self.v_vec_dend, 'r', label='dend')
		plt.xlabel('time (ms)')
		plt.ylabel('mV')
		plt.ylim(-80,40)
		plt.legend()
		# plt.ion()
		# plt.savefig('./plots/hw_07_Cell_'+str(cellId)+'_Voltage.png')
		plt.show()