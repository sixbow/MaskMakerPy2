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
filename = 'CKID_chipV1.cif'
# file with design parameters
design = np.loadtxt('partof_design_parameters.txt', skiprows = 1)

# enable symbol writing
gg.doSymbolWriting = True

layers = OrderedDict()
#layers = collections.OrderedDict()
layers['NbTiN_GND'] =  '0ff00ff00'
layers['SiC'] = '050000aa'
layers['NbTiN_Top'] = '0ff0000ff'
layers['Polyimide'] = '0ff0f000'
layers['Aluminum'] = '0fff0000'
layers['text'] = '05000000'

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
on_chip_name = "CKID V0.2" # Bruno: This text is written on the chip (in the Al layer), no apostrophes allowed
[lx,ly] = parts.Chipbasis.testchip20x4(layers, on_chip_name) # Bruno: writes chip outline, this is the size that we want for the microwave chip, lx = 20000, ly = 20000

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
# 
CPW_TL_W = 20
CPW_TL_S = 8

ro_line_dense = parts.CPWs.CPWreadout(CPW_TL_W, CPW_TL_S, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('Polyimide', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

ro_line_sparse = parts.CPWs.CPWreadout(CPW_TL_W, CPW_TL_S, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('Polyimide', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

# Display the TL properties.
print("W(line) TL is : {0}".format(str(ro_line_sparse.line)))
print("S(gap) TL is : {0}".format(str(ro_line_sparse.gap)))

#%%
#%% DRAW KIDs
connectors = [] # define an empty connector list
# Bruno: loop over all KIDs
ro_d = 20 # distance of top NbTiN plate to roline
L_caps_top = np.array([50.961 ,49.794 ,48.675 ,56.837 ,55.667 ,54.541 ,59.546 ,58.449 ,57.390 ,61.127 ,60.091 ,59.088]) # Plate length (or width), just 12 numbers that I randomly chose...
W_caps_top = L_caps_top
W_coupler = 4
L_coupler_overlap = np.array([5.50, 5.50, 5.50, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75]) # Oeff coupling sizes
W_CPW = np.array([0.5, 0.5, 0.5, 1, 1, 1, 2, 2, 2, 4, 4, 4]) # Width of the center line coupling sizes

for n in range(0,N_KIDs):
    moveto(kid_x[n], ly/2.) # Bruno: moves current coordinates (and the KID is drawn there)
    connectors = parts.PPCKIDs.Sietse_CKID(connectors, kid_spacing, n, ro_line_sparse, ro_d, L_caps_top[n], W_caps_top[n], W_coupler, L_coupler_overlap[n], W_CPW[n])

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