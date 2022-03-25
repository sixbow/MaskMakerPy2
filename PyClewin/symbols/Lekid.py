#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 11:43:15 2020

@author: kevink
"""

from PyClewin import *

import numpy as np

def draw_LEKID_symbol(inductor,capacitor,coupling_bar, coupling_bridge, pixel_x, pixel_y):
    gg.newSymbol('LEKID', top = False)

    dim_1 = 2*(inductor.N+1)*inductor.line + (2*inductor.N+1)*inductor.gap
    dim_2 = inductor.l_arm + 2*(inductor.line + inductor.gap)
    
    # start by drawing a circle at the LEKID focus.
    layername('text')
    circle(2)


    orientation = 1
    direction = orientation * 1j
    movedirection(-abs(orientation), dim_1/2 - inductor.line - inductor.gap/2)
    movedirection(orientation*-1j, dim_2/2 - inductor.sep - inductor.line)
    setmark('00')
    
    
    for n in range(0, inductor.N+1):
        layername('inductor')    
        if n == 0: #
            inductor.wirego(direction,inductor.l_arm-inductor.line - (inductor.sep - inductor.line - inductor.gap)) 
            inductor.square_180(direction, orientation)
        elif n == inductor.N and np.mod(n,2) == 1: # final bar and n is odd
            inductor.wirego(-direction,inductor.l_arm + inductor.line + inductor.gap)                
            inductor.end_bar(-direction)
        elif n == inductor.N and np.mod(n,2) == 0: #final bar and n is even
            inductor.wirego(direction,inductor.l_arm + inductor.line + inductor.gap) 
            inductor.end_bar(direction)
        elif np.mod(n,2) == 1:  #n is odd.
            inductor.wirego(-direction,inductor.l_arm) 
            inductor.square_180(-direction, orientation)
        elif np.mod(n,2) == 0: # n is even
            inductor.wirego(direction,inductor.l_arm) 
            inductor.square_180(direction, orientation)
        else: print "Something funky happend in the inductor logic"
            
    gomark('00')
    # since the first wire went into direction we go in - direction
    inductor.square_turn_go_widen(-direction, -abs(orientation), inductor.sep) 
    temp_inductor_gap = inductor.gap
    inductor.gap = inductor.sep
    inductor.wirego(-abs(orientation),inductor.leg)
    setmark('end_inductor')
    inductor.gap = temp_inductor_gap
    moveto(0.,0.)
    movedirection(abs(orientation), dim_1/2+inductor.sep_01)
    layername('NbTiN_GND')
    wire(-abs(orientation), pixel_x, pixel_y)
        
        
    #draw capacitor in a dummy layer
    layername('capacitor')
    gomark('end_inductor')
    
    ## draw the capacitor connector
    movedirection(-abs(orientation),capacitor.line/2)
    capacitor.wire_connector(abs(orientation),capacitor.capacitor_connector)
   
    ## draw the arms of the IDC
    capacitor.widen(-orientation)
    movedirection(-abs(orientation),capacitor.line/2)
    movedirection(-orientation*-1j, (capacitor.arm_a-capacitor.arm_b)/2)
    setmark('start_IDC')
    [x_idc,y_idc] = gg.position/1000 # not sure why the factor 1000 is here...
    capacitor.wirego(-abs(orientation),capacitor.N_fingers*capacitor.finger_line + capacitor.N_fingers*capacitor.finger_gap)
    setmark('end_IDC')
    
    ## Fingers of the capacitor
    gomark('start_IDC')
    movedirection(-orientation*1j,capacitor.gap/2)
    #capacitor.fingers_single(-orientation,N_fingers,finger_length, fshift[m_array,n_array],finger_cut,40)
    capacitor.fingers(-orientation)
    #capacitor.fingers_all(-orientation,capacitor.N_fingers,finger_length, fshift[m_array,n_array],finger_cut,[1,2,N_fingers-1,N_fingers])

    ## draw the connector bar
    gomark('end_IDC')
    movedirection(-orientation*1j,capacitor.line/2+capacitor.gap/2)
    #movedirection(-abs(orientation),finger_line/2)
    wirego(-abs(orientation), capacitor.finger_gap, capacitor.line)
    movedirection(-orientation*1j, capacitor.line/2)
    
    ## Draw the coupling bar 
    movedirection(-abs(orientation),coupling_bar.width/2)
    # coupling_bar(self,direction,length,width,d,width_bar,overlap,extension):        
    coupling_bar.bar(-orientation, 2*capacitor.line + capacitor.gap)
    # draw the coupling bridge
    movedirection(-orientation*1j, coupling_bridge.length_metal_coupling_bridge/2)
    #layername('Polyimide')
    #bar(orientation*1j, coupling_bridge.length_diel_coupling_bridge, coupling_bridge.width_diel_coupling_bridge)
    layername('inductor')
    bar(orientation*1j, coupling_bridge.length_metal_coupling_bridge, coupling_bridge.width_metal_coupling_bridge)
    
    return [x_idc, y_idc]
    
def IDC_mask(ID, x, y, capacitor, ldf):
        gg.newSymbol(ID, top = False)
        layername('text')
        #square(0)
        moveto(x,y)
        movedirection(1j,capacitor.gap/2 - capacitor.finger_gap)
        movedirection(-1,3.*capacitor.finger_gap + 2.5*capacitor.finger_line)
        wire(-1j, ldf, capacitor.finger_line)            
        for n in range(1,capacitor.N_fingers/2-2):
            movedirection(-1,2*capacitor.finger_gap + 2*capacitor.finger_line)
            wire(-1j, ldf, capacitor.finger_line)            

def draw_IDC_mask(symbol_name, ndf, ldf, x, y, mirror_dir):
    
    ldf_100 = 100*ldf
    ldf_10 = 10*ldf
    
    times_100 = int(np.floor(ndf/100))
    rem = np.fmod(ndf,100)
    times_10 = int(np.floor(rem/10))
    times_1 = int(np.fmod(rem,10))
    
    if mirror_dir == 'y':
        sign = 1
    else:
        sign = -1
    
    for i in range(0,times_100):
        placeSymbol('IDC_100', [x,y+sign*(i*ldf_100)], mirror =  mirror_dir)
    i = times_100
    for ii in range(0,times_10):
        placeSymbol('IDC_10', [x,y+sign*(i*ldf_100+ii*ldf_10)], mirror =  mirror_dir)
    ii = times_10
    for iii in range(0,times_1):
        placeSymbol('IDC_1', [x,y+sign*(i*ldf_100+ii*ldf_10+iii*ldf)], mirror = mirror_dir)

def IDC_mask_single(ID, x, y, capacitor, ldf):
        gg.newSymbol(ID, top = False)
        layername('text')
        #square(0)
        moveto(x,y)
        movedirection(-1j,capacitor.gap/2 - capacitor.finger_gap)
        movedirection(-1,2.*capacitor.finger_gap + 1.5*capacitor.finger_line)
        wire(1j, ldf, capacitor.finger_line)            
   
def draw_IDC_mask_single(symbol_name, ndf, ldf, x, y, mirror_dir, capacitor):
    
    x = x-5*(2*capacitor.finger_gap + 2*capacitor.finger_line)
    
    #ndf = 180.0
    max_cut = 86.0

    nr_whole_fingers = int(np.floor(ndf/max_cut))
    remaining_cut = np.fmod(ndf,max_cut)
    
    
    ldf_1000 = 1000*ldf
    ldf_100 = 100*ldf
    ldf_10 = 10*ldf
    
    
    times_1000 = int(np.floor(remaining_cut/(1000*ldf)))
    rem = np.fmod(remaining_cut,(1000*ldf))
    times_100 = int(np.floor(rem/(100*ldf)))
    rem = np.fmod(remaining_cut,(100*ldf))
    times_10 = int(np.floor(rem/(10*ldf)))
    rem = np.fmod(remaining_cut,(10*ldf))
    times_1 = int(np.round(rem/(1*ldf)))
    
    if mirror_dir == 'y':
        sign = -1
    else:
        sign = 1
    
    
    #first do whole fingers
    for n in range(0,nr_whole_fingers):
        placeSymbol('IDC_whole_finger',[x+n*(2*capacitor.finger_gap + 2*capacitor.finger_line) ,y], mirror = mirror_dir )
    
    if np.size(range(0,nr_whole_fingers)) == 0:
        n = -1
    
    for i in range(0,times_1000):
        placeSymbol('IDC_1000', [x+(n+1)*(2*capacitor.finger_gap + 2*capacitor.finger_line),y+sign*(i*ldf_1000)], mirror =  mirror_dir)
    i = times_1000
    for ii in range(0,times_100):
        placeSymbol('IDC_100', [x+(n+1)*(2*capacitor.finger_gap + 2*capacitor.finger_line),y+sign*(i*ldf_1000+ii*ldf_100)], mirror =  mirror_dir)
    ii = times_100
    for iii in range(0,times_10):
        placeSymbol('IDC_10', [x+(n+1)*(2*capacitor.finger_gap + 2*capacitor.finger_line),y+sign*(i*ldf_1000+ii*ldf_100+iii*ldf_10)], mirror = mirror_dir)
    iii = times_10
    for iiii in range(0,times_1):
        placeSymbol('IDC_1', [x+(n+1)*(2*capacitor.finger_gap + 2*capacitor.finger_line),y+sign*(i*ldf_1000+ii*ldf_100+iii*ldf_10 + iiii*ldf)], mirror = mirror_dir)
        
        
        
        
def Coupler_mask(ID, x, y, capacitor, coupling_bar, l_section):
        gg.newSymbol(ID, top = False)
        layername('text')
        
        moveto(x,y)
        movedirection(1j,capacitor.gap/2 + capacitor.line) ## Move up to the top edge of the capacitor
        movedirection(-1, capacitor.N_fingers*capacitor.finger_line + (capacitor.N_fingers+1)*capacitor.finger_gap + coupling_bar.width + coupling_bar.d + coupling_bar.width_bar/2)
        wire(-1j, l_section, coupling_bar.width_bar)
        
def draw_Coupler_mask(symbol_name, total_length, x, y, mirror_dir):
    
    times_100 = int(np.floor(total_length/100.0))
    rem = np.fmod(total_length,100.0)
    times_10 = int(np.floor(rem/10.0))
    times_1 = int(np.fmod(rem,10.0))

        
    if mirror_dir == 'y':
        sign = 1
    else:
        sign = -1
        
    for i in range(0,times_100):
        placeSymbol('Coupling_masker_100', [x,y+sign*(i*100)], mirror =  mirror_dir)
    i = times_100
    for ii in range(0,times_10):
        placeSymbol('Coupling_masker_10', [x,y+sign*(i*100+ii*10)], mirror =  mirror_dir)
    ii = times_10
    for iii in range(0,times_1):
        placeSymbol('Coupling_masker_1', [x,y+sign*(i*100+ii*10+iii*1)], mirror =  mirror_dir)   
        

def assign_readout_Marks(N_pixels, M_pixels, pitch, geo_cent, R):
    
    connectors = []
    
    geo_cent_x = geo_cent[0]
    geo_cent_y = geo_cent[1]
    
    if np.mod(M_pixels,2) == 0:
        loc_m_readout = np.linspace(-(M_pixels-1)*pitch/2, (M_pixels-3)*pitch/2, M_pixels/2) + pitch/2
        if np.mod(M_pixels,4) == 0:
            # in this case we need an extra row to wind back, we can decide if the spacing can be smaller for this row (pitch instead of 2*pitch)
            loc_m_readout = np.append(loc_m_readout,(M_pixels-1)*pitch/2 + pitch)  
            
    elif np.mod(M_pixels,2) == 1:
        # uneven and readout does wind back on top of last row
        loc_m_readout = np.linspace(-(M_pixels-1)*pitch/2, (M_pixels-1)*pitch/2, M_pixels) + pitch/2
    
    if np.mod(N_pixels,2) == 0:
            loc_n_readout = np.linspace(geo_cent_x - N_pixels/2*pitch, geo_cent_x + N_pixels/2*pitch, N_pixels+1)
        
    elif np.mod(N_pixels,2) == 1: 
            loc_n_readout = np.linspace(geo_cent_x - (pitch/2 + np.floor(N_pixels/2)*pitch), geo_cent_x + (pitch/2 + np.floor(N_pixels/2)*pitch), N_pixels+1)
    
    moveto(min(loc_n_readout) - 4*R - 200, 0)
    setmark('taper_in')
    go(200,-200)
    setmark('array_in')

    moveto(max(loc_n_readout + 4*R) + 200, 0)
    setmark('taper_out')
    go(-200,200)
    setmark('array_out')
    
    # place all the readout connector points in the array
    for m_array_readout in range(0,len(loc_m_readout)):
        for n_array_readout in range(0,len(loc_n_readout)):
            placeSymbol('array_bridge',[loc_n_readout[n_array_readout],loc_m_readout[m_array_readout]])
            moveto(loc_n_readout[n_array_readout],loc_m_readout[m_array_readout])
            if np.mod(m_array_readout,2) == 0 and (n_array_readout == 0 or n_array_readout == len(loc_n_readout)-1):
                setmark('KID'+'R'+str(m_array_readout)+'C'+(str(n_array_readout)))
                connectors.append(connector(1,'KID'+'R'+str(m_array_readout)+'C'+str(n_array_readout)))
            elif np.mod(m_array_readout,2) == 1 and (n_array_readout == 0 or n_array_readout == len(loc_n_readout)-1):
                setmark('KID'+'R'+str(m_array_readout)+'C'+(str(n_array_readout)))
                connectors.append(connector(-1,'KID'+'R'+str(m_array_readout)+'C'+str(n_array_readout)))


    for m in range(1,len(loc_m_readout),2):
        copy_list = connectors[m*(len(loc_n_readout)):(m+1)*(len(loc_n_readout))]    
        copy_list.reverse()
        connectors[m*(len(loc_n_readout)):(m+1)*(len(loc_n_readout))] = copy_list
        
    return connectors

def find_geo_centre(N_pixels, M_pixels, pitch, pixel_x, pixel_y,inductor,capacitor):
    loc_n = np.linspace(-(N_pixels-1)*pitch/2, (N_pixels-1)*pitch/2, N_pixels)
    loc_m = np.linspace(-(M_pixels-1)*pitch/2, (M_pixels-1)*pitch/2, M_pixels)
    # a few dimensions of the array
    space_x = pitch - pixel_x # space between the pixels in x
    space_y = pitch - pixel_y # space between the pixels in y
    array_x = N_pixels*pixel_x + (N_pixels-1)*space_x
    array_y = M_pixels*pixel_y + (M_pixels-1)*space_y
    size_array = np.array([array_x,array_y]) # estimate of the size of the array
    # dimensions of the inductor
    dim_1 = 2*(inductor.N+1)*inductor.line + (2*inductor.N+1)*inductor.gap
    dim_2 = inductor.l_arm + 2*(inductor.line + inductor.gap)
    # find the geometrical centre of the array
    geo_cent_y = 0 # the centre of the array in y is always zero
    if np.mod(N_pixels,2) == 1: #odd number of pixels in x
        geo_cent_x = -(pixel_x/2 - (dim_1/2 + inductor.sep_01))
    else:
        geo_cent_x = (pitch/2-(pixel_x/2 - (dim_1/2 + inductor.sep_01)))-pitch/2 
    geo_cent = np.array([geo_cent_x,geo_cent_y])
    return geo_cent