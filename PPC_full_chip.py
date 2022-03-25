#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 14:45:59 2020

A simple code for PPC kid array
options:
    - multiple KIDs based on design file
    - 2 Rows of KIDs
    
Designed for  20x20 chip size.

@author: kevink
"""

from PyClewin import *

import numpy as np
from collections import OrderedDict
import os
from copy import deepcopy as copy
import time as time
import matplotlib
import matplotlib.pyplot as plt

#%%
# save as:
filename = 'PPC_KIDS_feb_2022_Array.cif'
# file with design parameters
design = np.loadtxt('Full_PPC_3E4.txt', skiprows = 1)

# enable symbol writing
gg.doSymbolWriting = True

layers = OrderedDict()
layers = collections.OrderedDict()
layers['NbTiN_GND'] =  '0ff00ff00'
layers['aSi'] = '050000aa'
layers['NbTiN_line'] = '0ff0000ff'
layers['Polyimide'] = '0ff0f000'
layers['Aluminum'] = '0fff0000'
layers['text'] = '05000000'
layers['PPC_KID'] = '0f00cbff'


for k,v in layers.items():
    if k not in gg.layers.keys():
        gg.layers[k] = v
# Define the base unit for all lengths in the design
unit_scale = 1e3    # micron
mesh = 36
gg.scale = unit_scale

# Define and create chip
gg.newSymbol('Main', top = True)
on_chip_name = 'PPC Project 08-2020 Qc = 1E5'
[lx,ly] = parts.Chipbasis.testchip20x20(layers, on_chip_name)

## KID spacing
N_rows = 2 # work with even number of KIDs, i.e. 20 KIDs. Not tested for uneven KIDs
kid_spacing = 1000. # spacing in horizontal (x) direction between KIDs
kid_spacing_y = 3000. # spacing in vertical (y) direction between rows

## fins kid x and y locations
N_KIDs = int(design.shape[0])
row_A = [kid_spacing_y/2.] * int(np.floor(N_KIDs/2.))
row_B = [-kid_spacing_y/2.] * int(np.ceil(N_KIDs/2.))
kid_y = row_A + row_B
kid_y = ly/2. + np.array(kid_y)

if N_rows == 1:
    if np.mod(N_KIDs,2) == 1:
        kid_x = np.arange(-(np.floor(N_KIDs/2.)*kid_spacing), (np.floor(N_KIDs/2.)*kid_spacing)+1.0, kid_spacing)
        
    elif np.mod(N_KIDs,2) == 0:
        kid_x = np.arange(-((N_KIDs/2. - 0.5)*kid_spacing), ((N_KIDs/2. - 0.5)*kid_spacing)+1.0, kid_spacing)

if N_rows == 2:
    N_KIDs_row = N_KIDs/2
    if np.mod(N_KIDs_row,2) == 1:
        kid_x = np.arange(-(np.floor(N_KIDs_row/2.)*kid_spacing), (np.floor(N_KIDs_row/2.)*kid_spacing)+1.0, kid_spacing)
        kid_x = np.append(kid_x, kid_x)

        
    elif np.mod(N_KIDs_row,2) == 0:
        kid_x = np.arange(-((N_KIDs_row/2. - 0.5)*kid_spacing), ((N_KIDs_row/2. - 0.5)*kid_spacing)+1.0, kid_spacing)
        kid_x = np.append(kid_x, kid_x)
    
kid_x = lx/2. + np.array(kid_x)

#%% Readoutline
ro_line_sparse = parts.CPWs.CPWreadout(10, 5, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('Polyimide', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

ro_line_dense = parts.CPWs.CPWreadout(10, 5, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('Polyimide', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

#%% DRAW KIDs

connectors = [] # define an empty connector list

for n in range(0,N_KIDs):
        
    if N_rows == 2: # if two rows kids have different y locations
        if n == N_KIDs/2.: # we need an extra connector in the centre to route the readoutline
            moveto(lx/2., ly/2.)
            setmark('KID_extra_a')
            connectors.append(base.connector(-1,'KID_extra_a'))     
        moveto(kid_x[n], kid_y[n])
    elif N_rows == 1: # just one line of KIDs as same y_loc
        moveto(kid_x[n], ly/2.)
    else: # for now only single or double row designs
        sys.exit('Number of rows ('+ str(N_rows) + ') not supported')

    connectors = parts.PPCKIDs.PPCkid_v8(-1j, design[n,1], design[n,2], design[n,3], design[n,4], design[n,5], design[n,6], ro_line_sparse, kid_spacing, layers, connectors, n)
    
    
## if we use two rows we need an extra readout marker to make sure the readout line exits the array correctly
if N_rows == 2:
    moveto(kid_x[n], kid_y[n])
    go(2*kid_spacing,0)
    setmark('KID_extra_b')
    connectors.append(base.connector(1,'KID_extra_b'))

## Bondpasa and readout
gomark('bondpadleft')
parts.Readout.bondpad_100nm_alu(-1, ro_line_sparse, x2m('chip00'))

ro_line_sparse.connect(connectors[0])


for i in range(1,len(connectors)):
    ro_line_dense.connect(connectors[i])

ro_line_sparse.connect(base.connector(1, 'bondpadright'))

gomark('bondpadright')
parts.Readout.bondpad_100nm_alu(1, ro_line_sparse, x2m('chipFF'))

#write file
writeTotalString(filename)