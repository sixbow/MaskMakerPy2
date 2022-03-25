#%%
from PyClewin import gg, parts, moveto, gomark, x2m, base, writeTotalString
## gg (script) is a short name for the 'script' class that contains the layers, connectors, the methods etc. 
## parts (parts) are pre-defined parts
## moveto (script) moves the current position (this is where patterns are 'written')
## gomark (script) moves the current position to the 'mark' position (self.mark), I think marks are a way to store locations (and rotations) in a dict format
## x2m (base > ucs) returns the 'x' of the distance to mark vector, it uses dist2mark from (script)
import numpy as np
from collections import OrderedDict # This is a dictionary where the key-value pairs are ordered

#%%
filename = 'test.cif'
# file with design parameters
design = np.loadtxt('design_bruno.txt', skiprows = 1)

# enable symbol writing
gg.doSymbolWriting = True

layers = OrderedDict()
#layers = collections.OrderedDict()
layers['SiN'] =  '067000aa'
layers['NbTiN_GND'] =  '0ff00ff00'
layers['SiC'] = '050000aa'
layers['NbTiN_line'] = '0ff0000ff'
layers['Polyimide'] = '0ff0f000'
layers['Aluminum'] = '0fff0000'
layers['text'] = '05000000'
layers['PPC_KID'] = '0f00cbff'

# Bruno: Add the layers to the gg object 
for k,v in layers.items():
    if k not in gg.layers.keys():
        gg.layers[k] = v
# Define the base unit for all lengths in the design
unit_scale = 1e3    # micron
mesh = 36           # Bruno: resolution of polygon used for readout line corners
gg.scale = unit_scale

# Define and create chip
gg.newSymbol('Main', top = True) # Bruno: Not sure what 'top' is, I think it is probably a symbol hierarchy (so you can have symbols inside symbols)
on_chip_name = "Sietse test chip" # Bruno: This text is written on the chip (in the Al layer), no apostrophes allowed
[lx,ly] = parts.Chipbasis.testchip20x20(layers, on_chip_name) # Bruno: writes chip outline, this is the size that we want for the microwave chip, lx = 20000, ly = 20000

## KID spacing
kid_spacing = 1000. # spacing in horizontal (x) direction between KIDs

## Determine kid x and y locations
N_KIDs = int(design.shape[0])

if np.mod(N_KIDs,2) == 1: # uneven number of KIDs
    kid_x = np.arange(-(np.floor(N_KIDs/2.)*kid_spacing), (np.floor(N_KIDs/2.)*kid_spacing)+1.0, kid_spacing)

elif np.mod(N_KIDs,2) == 0: # even number of KIDs
    kid_x = np.arange(-((N_KIDs/2. - 0.5)*kid_spacing), ((N_KIDs/2. - 0.5)*kid_spacing)+1.0, kid_spacing)
    
kid_x = lx/2. + np.array(kid_x) # Array of x-positions of KIDs (microns)

#%%
#%% Readoutline
# Bruno: It seems that ro_line_sparse and ro_line_dense are exactly the same 
ro_line_dense = parts.CPWs.CPWreadout(10, 5, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('Polyimide', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

ro_line_sparse = parts.CPWs.CPWreadout(10, 5, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('Polyimide', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

#%%
#%% DRAW KIDs
connectors = [] # define an empty connector list
# Bruno: loop over all KIDs
ro_d = 20 # distance of top NbTiN plate to roline
L_caps_top = np.array([20, 30, 40, 60, 70, 80, 100, 110, 120, 140, 150, 160]) # Plate length (or width), just 12 numbers that I randomly chose...
W_caps_top = L_caps_top
W_coupler = 4
L_coupler_overlap = 4
W_CPW = 2
for n in range(0,N_KIDs):
    moveto(kid_x[n], ly/2.) # Bruno: moves current coordinates (and the KID is drawn there)
    connectors = parts.PPCKIDs.Sietse_testKID(connectors, kid_spacing, n, ro_line_sparse, ro_d, L_caps_top[n], W_caps_top[n], W_coupler, L_coupler_overlap, W_CPW)

#%%
## DRAW Bondpads and readout
gomark('bondpadleft')
parts.Readout.bondpad_100nm_alu(-1, ro_line_sparse, x2m('chip00'))

ro_line_sparse.connect(connectors[0])


for i in range(1,len(connectors)):
    ro_line_dense.connect(connectors[i])

ro_line_sparse.connect(base.connector(1, 'bondpadright'))

gomark('bondpadright')
parts.Readout.bondpad_100nm_alu(1, ro_line_sparse, x2m('chipFF'))

#%%
#write file
writeTotalString(filename)