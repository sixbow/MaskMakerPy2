#%%
from PyClewin import gg, parts, moveto, gomark, x2m, base, writeTotalString
## gg (script) is a short name for the 'script' class that contains the layers, connectors, the methods etc. 
## parts (parts) are pre-defined parts
## moveto (script) moves the current position (this is where patterns are 'written')
## gomark (script) moves the current position to the 'mark' position (self.mark), I think marks are a way to store locations (and rotations) in a dict format
## x2m (base > ucs) returns the 'x' of the distance to mark vector, it uses dist2mark from (script)
import numpy as np
from collections import OrderedDict # This is a dictionary where the key-value pairs are ordered


#Klayout_lyp_gen function (Part 1)
from xml.dom.minidom import Document
def Klayout_lyp_gen(layers, file_name='Klayout_layer_properties.lyp'):
    """Klayout_lyp_gen(layers, file_name= 'Klayout_layer_properties.lyp')
    Reads layer dictionary and writes .lyp file for use in Klayout.

    Parameters:
    argument1 (Ordered dict): layers file from PyClewin
    argument2 (string): file name used to write layer properties to 
    default: Klayout_layer_properties.lyp
    Example: filename[:-4]+'.lyp'    |  this way filename can be 'MyChip.cif' and then layer file becomes 'MyChip.lyp'

    Returns:
    Nothing!
    Side Effect: Writes .lyp file for use in Klayout

   """
    
    dict_length = len(layers.keys()) # Obtains the length of the user defined dict. 
    layer_index_arr = list(range(0,dict_length))
    fill_lookup = OrderedDict()
    fill_lookup['f'] = 'I0'
    fill_lookup['3'] = 'I9'
    fill_lookup['2'] = 'I5'
    fill_lookup['5'] = 'I4' # Double hatch is converted to tight hatching in Klayout because Klayout does not have this option.
    out_lookup = OrderedDict()
    out_lookup['0'] = 'I0'
    out_lookup['1'] = 'I6'
    out_lookup['2'] = 'I4'
    out_lookup['3'] = 'I5'
    out_lookup['4'] = 'I3'
    try:
        doc = Document()

        root = doc.createElement('layer-properties')
        doc.appendChild(root)
        #layer_index_arr = ['0','1','2','4','5','8','9']
        #name_arr = ['NbTiN_GND','SiC','NbTiN_Top','Aluminium','text','E-beam_Alu','2inch Circle']
        #color_arr = ['#ffa500','#A908B5','#ff4500','#0000ff','#gggg00','#44gg00','#0044gg']
        #pattern_arr = ['I0','I9','I0','I0','I4','I5','I1']
        for i in range(dict_length):
            #Begin: This block makes the name property for a layer.
            KL_layers = doc.createElement('properties')
            root.appendChild(KL_layers)
            subKL_layers = doc.createElement('name')
            KL_layers.appendChild(subKL_layers)
            text = doc.createTextNode(layers.keys()[i])
            subKL_layers.appendChild(text)
            subKL_layers = doc.createElement('frame-color')
            KL_layers.appendChild(subKL_layers)
            text = doc.createTextNode('#'+layers.values()[i][2:8][::-1])
            subKL_layers.appendChild(text)
            subKL_layers = doc.createElement('fill-color')
            KL_layers.appendChild(subKL_layers)
            text = doc.createTextNode('#'+layers.values()[i][2:8][::-1])
            subKL_layers.appendChild(text)
            subKL_layers = doc.createElement('dither-pattern')
            KL_layers.appendChild(subKL_layers)
            text = doc.createTextNode(fill_lookup[layers.values()[i][1]])
            subKL_layers.appendChild(text)
            subKL_layers = doc.createElement('line-style')
            KL_layers.appendChild(subKL_layers)
            text = doc.createTextNode(out_lookup[layers.values()[i][0]])
            subKL_layers.appendChild(text)
            subKL_layers = doc.createElement('source')
            KL_layers.appendChild(subKL_layers)
            text = doc.createTextNode(str(layer_index_arr[i])+'/0@1')
            subKL_layers.appendChild(text)
            #End: of property ("Layer") block.

        # End of the document contains empty name 
        placehold_name = doc.createElement('name')
        root.appendChild(placehold_name)
        xml_str = doc.toprettyxml(indent ="\t") 
        
        
        with open(file_name, "w") as f:
            f.write(xml_str) 
        print('Klayout-lyp-gen-addon: Succes! wrote: '+file_name)
    
    except Exception,e: print("Klayout-lyp-gen-addon:"+str(e)+"\n Klayout-lyp-gen-addon: Whoops-a-daisy. These are not supported parameters for Klayout-lyp-gen-addon!. Not generating lyp file")
#/Klayout_lyp_gen function (End Part 1)



#%%
filename = 'CKID_chipV1.cif'
# file with design parameters
design = np.loadtxt('partof_design_parameters.txt', skiprows = 1)

# enable symbol writing
gg.doSymbolWriting = True

layers = OrderedDict()
#layers = collections.OrderedDict()
layers['NbTiN_GND'] =  '0f00ff00'
layers['SiC'] = '050000aa'
layers['NbTiN_Top'] = '0f0000ff'
layers['Polyimide'] = '0ff0f000'
layers['Aluminum'] = '0fff0000'
layers['text'] = '05000000'


#Calling the lyp_gen. (Part 2) - This needs to be done after definition of layers, save_path_file
save_path_file = "my_Klayout_layersV0.lyp" #Name of the xml file
Klayout_lyp_gen(layers,filename[:-4]+'.lyp')
#Calling the lyp_gen. (Part 2)



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
on_chip_name = "CKID V1.0" # Bruno: This text is written on the chip (in the Al layer), no apostrophes allowed
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
CPW_TL_S = 6

ro_line_dense = parts.CPWs.CPWreadout(CPW_TL_W, CPW_TL_S, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('SiC', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
                                bridgeDistance = 1e3)

ro_line_sparse = parts.CPWs.CPWreadout(CPW_TL_W, CPW_TL_S, mesh, 200, 'NbTiN_GND', 'text',
                                parts.Bridges.Bridge('SiC', 'Aluminum', 30.0, 40.0, 65.0, 20.0),
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
W_CPW = np.array([6, 6, 6, 6, 6, 6, 2, 2, 2, 4, 4, 4]) # Width of the center line 
S_CPW = np.array([-2, -2, -2 ,-1.5 ,-1.5 ,-1.5 , 2, 2, 2, 4, 4, 4]) # Width of the center line :: S = (Tot_width - W_CPW)/2
for n in range(0,N_KIDs):
    moveto(kid_x[n], ly/2.) # Bruno: moves current coordinates (and the KID is drawn there)
    connectors = parts.PPCKIDs.Sietse_CKID(connectors, kid_spacing, n, ro_line_sparse, ro_d, L_caps_top[n], W_caps_top[n], W_coupler, L_coupler_overlap[n], W_CPW[n] , S_CPW[n])

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