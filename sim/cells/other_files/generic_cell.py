#! /usr/bin/python3

from CellClass import HHCell
from neuron import h

'''
# Method 1: creating 'generic_cell' class as an instance of 'HHCell' class
'''
# class definition
class generic_cell(HHCell):
    # constructur method
    def __init__(self):
        HHCell.__init__(self)
        

    # Example of how to change a particular property of HHCell
    # self.soma.L = 10000

'''
# Method 2: creating an instance of 'HHCell' class in a 'cell' object within the 'generic_cell' class
'''
# # class definition
# class generic_cell():
#     # constructur method
#     def __init__(self):
#         # instance of cell from HHCell class
#         self.cell = HHCell() 

#     # Example of how to change a particular property of HHCell
#     # self.cell.soma.L = 10000


