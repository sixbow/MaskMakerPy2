#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 09:55:37 2020

@author: kevink
"""

from PyClewin import *
from PyClewin.base import *
import numpy as np
import scipy.constants as spc
import CPWs

def Sietse_CKID(connectors, distance_kids, n, ro_line, ro_d, L_cap_top, W_cap_top, W_coupler, L_coupler_overlap, W_CPW):
    #Edit_Sietse: I think this should not be here!! #from PyClewin import *
        
    # Make connectors, I think we need 3 connectors per KID to make sure that the bridges won't overlap with the coupler
    setmark('KID_sym_center')
    
    movedirection(-1,distance_kids/2)
    setmark('KID'+str(n+1)+'in')
    connectors.append(base.connector(1,'KID'+str(n+1)+'in'))
    
    gomark('KID_sym_center')
    setmark('KID'+str(n+1))
    connectors.append(base.connector(1,'KID'+str(n+1)))
    
    movedirection(1,distance_kids/2)
    setmark('KID'+str(n+1)+'out')
    connectors.append(base.connector(1,'KID'+str(n+1)+'out'))
    ro_line.bridgeClass.draw(1, ro_line.line, ro_line.gap)
    
    # Write KID
        # Parameters
    L_TLtoPPC = 20 #<- User variable!
    L_OrigintoMSL = (ro_line.line/2) - L_coupler_overlap # Calculated from given readout line.
    SiC_padding = 6 #<- User variable!
    L_connectfromSiC = 6 #<- User variable!
    W_NbTiN_Top_via = 4 #<- User variable!
    L_wideslot_padding = 2 #<- User variable!
    SiC_padding_top = ro_line.gap # User variable
    W_wideslot_width = 3*W_NbTiN_Top_via # Calculated
    S_CPW  = W_CPW # Calculated
    L_shortoverlap = 3 #<- User variable! Overlap of the short on the end of the readout line.
    L_CPWtarget = 1000 #<- User variable(Change this if you want)!  This is the user adaptable target length of the cpw section. 
    L_CPWslot = L_CPWtarget - L_connectfromSiC # Calculated
    L_viaoverlap = L_connectfromSiC/2
    L_Al = L_viaoverlap  + L_wideslot_padding + L_CPWslot + L_shortoverlap # Calculated
    L_SiC = SiC_padding + L_cap_top + L_TLtoPPC + (2*ro_line.gap) + ro_line.line + SiC_padding_top
    W_SiC = 3*W_cap_top  + 2*SiC_padding
    #SiC_margin = 40 
    #SiC_bottom_L = 15
    #NbTiN_SiN_L_overlap = 20
    #Al_SiN_L_overlap = 20
    # SiN_d = -4
    # SiN_L = 30
    # SiN_W = 20
        # Process Bias for optical nanofabrication [um] +is outward(bigger then design value) and -is inward (smaller than design value) mask
    pbNbTiN_GNDx = 0
    pbNbTiN_GNDy = 0
    pbNbTiN_Topx = 0
    pbNbTiN_Topy = 0
    print("NbTiN_GND process bias[um](x-direction) = {0}".format(pbNbTiN_GNDx) )
    print("NbTiN_GND process bias[um](y-direction) = {0}".format(pbNbTiN_GNDx) )
    print("NbTiN_Top process bias[um](x-direction) = {0}".format(pbNbTiN_Topx) )
    print("NbTiN_Top process bias[um](y-direction) = {0}".format(pbNbTiN_Topx) )


    # We don't use any process bias for the TL and the SiC layer because dimentions are not critical. The process bias for the TL can be accounted for by changing
    # the L_coupler_overlap (Overlap of the TL)

    # Draw Microstrip line that connects the Throughline(TL) with the Parrallel plate capacitor(PPC).
    # Begin position relative to KID_sym_center (This is the middle of the TL line.).
    # -j( width TL signal/2  - Oeff (this is the overlap)) in the -y direction
    # Begin writing: MSL
    layername('NbTiN_Top')
    gomark('KID_sym_center') # First we reset the cursor to the origin(Middle of TL)
    movedirection(-1j, L_OrigintoMSL)# Set cursus on beginning of the MSL target value.
    setmark('KID_begin_MSL_target')
    movedirection(-1j, -pbNbTiN_Topy)# Set cursus on beginning of the MSL print value.
    setmark('KID_begin_MSL_print')
    L_MSL = L_coupler_overlap + ro_line.gap + L_TLtoPPC  # This is the lenght that the MSL should be. 
    wire(-1j, L_MSL, 4+(2*pbNbTiN_Topx)) # Makes the MSL.
    # End writing: MSL
    # 
    # Begin writing: PPC
    layername('NbTiN_Top')
    gomark('KID_begin_MSL_target')
    movedirection(-1j,L_MSL)
    setmark('KID_begin_PPC_target')
    movedirection(-1j, -pbNbTiN_Topy)
    setmark('KID_begin_PPC_print')
    wire(-1j, L_cap_top + (2*pbNbTiN_Topy), W_cap_top + (2*pbNbTiN_Topx))
    # End writing: PPC
    #  
    # Begin writing: NbTiN via/slope connector
    layername('NbTiN_Top')
    gomark('KID_begin_PPC_target')
    movedirection(-1j, L_cap_top  )
    setmark('KID_end_PPC_target')
    movedirection(-1j, pbNbTiN_Topy )
    setmark('KID_end_PPC_print')
    wirego(-1j,SiC_padding + L_connectfromSiC , W_NbTiN_Top_via+pbNbTiN_Topx)
    setmark('KID_end_NbTiNvia_print')
    movedirection(-1j, -pbNbTiN_Topy)
    setmark('KID_end_NbTiNvia_target')
    
    # End writing: NbTiN via/slope connector

    # Begin writing: Wide slot NbTiN_GND slot
    layername('NbTiN_GND')
    gomark('KID_end_PPC_target')
    setmark('KID_begin_wideslot_target')
    movedirection(-1j,-pbNbTiN_GNDy)
    setmark('KID_begin_wideslot_print')
    wire(-1j, SiC_padding + L_connectfromSiC + L_wideslot_padding + (2*pbNbTiN_GNDy) , W_wideslot_width + (2*pbNbTiN_GNDx))
    movedirection(-1j, SiC_padding + L_connectfromSiC + L_wideslot_padding )
    setmark('KID_end_wideslot_target')
    movedirection(-1j, pbNbTiN_GNDy )
    setmark('KID_end_wideslot_print')
    # End writing: Wide slot NbTiN_GND slot

    # Begin writing: Hybrid CPW slot (CPWslot: 2S+W)
    layername('NbTiN_GND')
    gomark('KID_end_wideslot_target')
    setmark('KID_begin_CPWslot_target')
    movedirection(-1j,(2*pbNbTiN_GNDy))
    setmark('KID_begin_CPWslot_print')
    wire(-1j, L_CPWslot + pbNbTiN_GNDy, (2*S_CPW+W_CPW)+(2*pbNbTiN_GNDx))
    movedirection(-1j, L_CPWslot - (2*pbNbTiN_GNDy))
    setmark('KID_end_CPWslot_target')
    # End writing: Hybrid CPW slot 

    # Begin writing: Al line 
    layername('Aluminum')
    gomark('KID_end_NbTiNvia_target')
    movedirection(-1j, -L_viaoverlap)
    wire(-1j, L_Al, W_CPW)
    # End writing: Al line
    
    # Begin writing: SiC Dielectric patch. (Warning writing in the other direction 1j direction (+y))
    layername('SiC')
    gomark('KID_end_PPC_target')
    movedirection(-1j, SiC_padding) # Now we are where the SiC dielectric patch should start.
    wire(1j, L_SiC, W_SiC) # Warning this is in the +y direction (+j direction)
    # End writing: SiC Dielectric patch.







    #     # NbTiN top 
    # layername('NbTiN_line')
    #         # Coupler
    # gomark('KID_sym_center')
    # movedirection(-1j, ro_line.line/2 - L_coupler_overlap)
    # L_coupler = ro_d + ro_line.slot + L_coupler_overlap
    # wire(-1j, L_coupler, W_coupler)
    #         # Parallel plate
    # gomark('KID_sym_center')
    # ro_line_width = 2 * ro_line.slot + ro_line.line
    # movedirection(-1j, ro_line_width/2 + ro_d)
    # wire(-1j, L_cap_top, W_cap_top)
    #         # Connection with CPW
    # gomark('KID_sym_center')
    # movedirection(-1j, ro_line_width/2 + ro_d + L_cap_top)
    # wire(-1j, SiC_bottom_L + NbTiN_SiN_L_overlap + SiN_d, W_CPW)
    #    # Al
    # layername('Aluminum')
    # movedirection(-1j, SiN_L - Al_SiN_L_overlap)
    # wire(-1j, L_Al, W_CPW)
    #     # SiC
    # layername('SiC')
    # gomark('KID_sym_center')
    # movedirection(1j, ro_line_width/2 + SiC_margin)
    # wire(-1j, L_cap_top + ro_line_width + ro_d + SiC_margin + SiC_bottom_L, W_cap_top + 2*SiC_margin)
    #     # CPW slot NbTiN_GND Hybrid section 
    #     #
    # #ViaGap_L = ro_line_width/2 + ro_d + L_cap_top +SiC_bottom_L + SiN_d  + SiN_L - Al_SiN_L_overlap - (ro_line_width/2 + L_coupler + L_cap_top)
    # layername('NbTiN_GND')
    # gomark('KID_sym_center')
    # #movedirection(-1j, ro_line_width/2 + L_coupler + L_cap_top)
    # movedirection(-1j, ro_line_width/2 + ro_d + L_cap_top)
    # wire(-1j, L_Al  , 3*W_CPW)
    # print (ro_line_width/2 + L_coupler + L_cap_top)    

    return connectors


def PPCkid_v6(direction, CAP_bot, CAP_top, N, L_arm, arm_spacing, arm_gap, W_inductor, offset, diel_spacing, bottom_layer, diel_layer, top_layer, mesh, ro_line):
    """
    direction:
    CAP_bot:        Bottom electrode size (x,y)
    CAP_top:        Top electrode size (x,y)
    N:              Number of inductor sections
    L_arm:          Inductor arm size
    arm_spacing:    Spacing between arms
    arm_gap:        Gap between left and right arm
    W_inductor:     Inductor line width
    offset:         Distance between readout line and first inductor line
    diel_spacing:
    bottom_layer:
    diel_layer:
    top_layer
    """
    
    ## required lines
    CPW_0 = CPWs.CPW(0., (L_arm)/2., mesh, 120, 'PPC_KID')
    CPW_A = CPWs.CPW(L_arm - 2.*W_inductor, W_inductor, mesh, 120, 'PPC_KID')
    CPW_B = CPWs.CPW(arm_gap, (L_arm-arm_gap)/2., mesh, 120, 'PPC_KID')
    CPW_C = CPWs.CPW(arm_gap, W_inductor, mesh, 120, 'PPC_KID')
       
    
    spacing = ro_line.line/2. + ro_line.gap + offset
    layername('PPC_KID')
    movedirection(direction,spacing)
    #first bar
    CPW_0.wirego(direction,W_inductor)
    # first section (drawn even when N = 0)
    CPW_A.wirego(direction,arm_spacing)
    CPW_B.wirego(direction,W_inductor)
    # draw N [small, widen, wide, narrow] sections
    for n in range(0,N):
        CPW_C.wirego(direction,arm_spacing)
        CPW_B.wirego(direction,W_inductor)
        CPW_A.wirego(direction,arm_spacing)
        CPW_B.wirego(direction,W_inductor)
    
    ## connector section
    wire(direction, 10., W_inductor, shift=(0,(arm_gap/2. + W_inductor/2.)))
    wirego(direction, 15., W_inductor, shift=(0,-(arm_gap/2. + W_inductor/2.)))
    
    ## Plates
    wire(direction, CAP_bot[0], CAP_bot[1])
    
    layername('NbTiN_line')
    wire(direction, CAP_top[0], CAP_top[1])
    wire(-direction,10.,W_inductor-2,shift=(0,-(arm_gap/2. + W_inductor/2.)))
    
    layername('Polyimide')
    wire(direction, CAP_bot[0]+diel_spacing, CAP_bot[1]+diel_spacing , shift=(-diel_spacing/2.,0))
    
def PPCkid_v7(direction, L_cap, W_cap, overlap, N_inductor, L_inductor, L_NBTIN_gap, ro_line, distance_kids, layers, connectors, n):
    #Edit_Siets: I think this should not be here!! #from PyClewin import *

    
    L_cap_top = L_cap
    W_cap_top = W_cap
    
    L_cap_bot = L_cap
    W_cap_bot = W_cap
    
    gap_space = 20.0
    W_NBTIN_gap = L_cap_top + 2*gap_space
    
    kid_spacing = 37.5
    
    sep_coupling_bar = 6.0
    width_coupling_bar = 5.0
    width_coupling_bar_2 = 3.0

    width_coupling_bridge = 6.0
    length_coupling_bridge = 33.0
    centre_offset_coupling_bridge = 3.0
    bridge_coupler_overlap = 8.0
        
    length_bridge_diel = 24.0
    offset_diel = (length_coupling_bridge - length_bridge_diel)/2
    width_bridge_diel = 2*12.0 + width_coupling_bridge
    
    setmark('KID_sym_center')
    
    movedirection(-1,distance_kids/2)
    setmark('KID'+str(n+1)+'in')
    connectors.append(base.connector(1,'KID'+str(n+1)+'in'))
    
    gomark('KID_sym_center')
    setmark('KID'+str(n+1))
    connectors.append(base.connector(1,'KID'+str(n+1)))
    
    movedirection(1,distance_kids/2)
    setmark('KID'+str(n+1)+'out')
    connectors.append(base.connector(1,'KID'+str(n+1)+'out'))
    ro_line.bridgeClass.draw(1, ro_line.line, ro_line.gap)
    
    
    gomark('KID_sym_center')

    movedirection(1, 0.5*W_cap_top + sep_coupling_bar + 0.5*width_coupling_bar)
    setmark('start_coupling_bar')
    movedirection(-direction, centre_offset_coupling_bridge)
    
    ## Bridge over readoutline
    layername('Polyimide')
    wire(direction, length_bridge_diel, width_bridge_diel, shift=(offset_diel,0))    
    layername('Aluminum')
    wire(direction,6,20)
    wirego(direction, length_coupling_bridge, width_coupling_bridge)
    movedirection(-direction, bridge_coupler_overlap)
    
    ## Coupling bar
    layername('PPC_KID')
    length_start_bar = kid_spacing - (length_coupling_bridge - centre_offset_coupling_bridge - bridge_coupler_overlap)
    wirego(direction, length_start_bar, width_coupling_bar)
    wire(direction, overlap, width_coupling_bar)
    
    layername('NbTiN_line')
    wire(direction, overlap, width_coupling_bar_2)
    movedirection(direction,0.5*width_coupling_bar_2)
    movedirection(-1,0.5*width_coupling_bar_2)
    wirego(-1, sep_coupling_bar + 0.5*(width_coupling_bar - width_coupling_bar_2), width_coupling_bar_2)
    
    ## Capacitor
    gomark('KID_sym_center')
    movedirection(direction, kid_spacing)
    wire(direction, L_cap_top, W_cap_top)
    
    layername('PPC_KID')
    wire(direction, L_cap_bot, W_cap_bot)
    
    layername('aSi')
    extra_diel_x = 15.0
    extra_diel_y = 5.0
    wire(direction, L_cap_bot+2*extra_diel_y, W_cap_bot+2*extra_diel_x, shift=(-extra_diel_y,0))

    ## gap in NbTiN
    layername('NbTiN_GND')
    wire(direction, L_NBTIN_gap, W_NBTIN_gap, shift=(-gap_space, - (L_cap - W_cap)/2))
    
    ## Inductor attempt
    inductor_line = 3.0
    inductor_gap = 2.0
    large_gap = 9.0
    
    N = int(N_inductor);
    last_direction = -1
    L_ind = L_inductor
    
    movedirection(direction, L_cap)
    movedirection(1, W_cap/2)
    setmark('lower_corner')
    
    ## start of inductor
    movedirection(-1,large_gap+1.5*inductor_line)
    layername('NbTiN_line')
    wirego(direction,19,inductor_line)
    movedirection(-direction, 8)
    layername('PPC_KID')
    wirego(direction,10,inductor_line+2.0)
    
    
    gomark('lower_corner')
    movedirection(-1,inductor_line/2)
    layername('PPC_KID')
    wirego(direction, 26, inductor_line )
    movedirection(direction,inductor_line/2)
    movedirection(1,inductor_line/2)
    wirego(-1,11,inductor_line)

    ## CPW like inductor
    inductor_base = parts.CPWs.CPW(inductor_gap, inductor_line, 36, 10, 'PPC_KID')
    movedirection(-direction, inductor_gap/2 + inductor_line/2)
    inductor_base.wirego(-1,L_ind-3)
    

    
    for nx in range(1,N):
        direction_out = inductor_base.square_turn_180_go(last_direction,-1j)
        inductor_base.wirego(direction_out,L_ind)
        last_direction = direction_out
        
    inductor_base.wirego(last_direction, inductor_line*2 + inductor_gap)
    wire(-last_direction,inductor_line,inductor_gap)

    return connectors
    
def PPCkid_v8(direction, L_cap, W_cap, overlap, N_inductor, L_inductor, L_NBTIN_gap, ro_line, distance_kids, layers, connectors, n):
    #Edit_Siets: I think this should not be here!! #from PyClewin import *

    
    L_cap_top = L_cap
    W_cap_top = W_cap
    
    L_cap_bot = L_cap + 8.0
    W_cap_bot = W_cap + 8.0
    
    
    
    gap_space = 22.0
    W_NBTIN_gap = L_cap_bot + 2*gap_space
    
    
    
    kid_spacing = 37.5 + 6.0
    
    sep_coupling_bar = 6.0
    width_coupling_bar = 5.0
    width_coupling_bar_2 = 3.0

    width_coupling_bridge = 6.0
    length_coupling_bridge = 33.0
    centre_offset_coupling_bridge = 3.0
    bridge_coupler_overlap = 8.0
        
    length_bridge_diel = 24.0
    offset_diel = (length_coupling_bridge - length_bridge_diel)/2
    width_bridge_diel = 2*12.0 + width_coupling_bridge
    
    setmark('KID_sym_center')
    
    movedirection(-1,distance_kids/2)
    setmark('KID'+str(n+1)+'in')
    connectors.append(base.connector(1,'KID'+str(n+1)+'in'))
    
    gomark('KID_sym_center')
    setmark('KID'+str(n+1))
    connectors.append(base.connector(1,'KID'+str(n+1)))
    
    movedirection(1,distance_kids/2)
    setmark('KID'+str(n+1)+'out')
    connectors.append(base.connector(1,'KID'+str(n+1)+'out'))
    ro_line.bridgeClass.draw(1, ro_line.line, ro_line.gap)
    
    
    gomark('KID_sym_center')

    movedirection(1, 0.5*W_cap_top + sep_coupling_bar + 0.5*width_coupling_bar)
    setmark('start_coupling_bar')
    movedirection(-direction, centre_offset_coupling_bridge)
    
    ## Bridge over readoutline
    layername('Polyimide')
    wire(direction, length_bridge_diel, width_bridge_diel, shift=(offset_diel,0))    
    layername('Aluminum')
    wire(direction,6,20)
    wirego(direction, length_coupling_bridge, width_coupling_bridge)
    movedirection(-direction, bridge_coupler_overlap)
    
    ## Coupling bar
    layername('PPC_KID')
    length_start_bar = kid_spacing - (length_coupling_bridge - centre_offset_coupling_bridge - bridge_coupler_overlap)
    wirego(direction, length_start_bar, width_coupling_bar)
    wire(direction, overlap, width_coupling_bar)
    
    layername('NbTiN_line')
    wire(direction, overlap, width_coupling_bar_2)
    movedirection(direction,0.5*width_coupling_bar_2)
    movedirection(-1,0.5*width_coupling_bar_2)
    wirego(-1, sep_coupling_bar + 0.5*(width_coupling_bar - width_coupling_bar_2), width_coupling_bar_2)
    
    ## Capacitor
    gomark('KID_sym_center')
    movedirection(direction, kid_spacing)    
    wire(direction, L_cap_top, W_cap_top)
    
    layername('PPC_KID')
    movedirection(-direction, (L_cap_bot-L_cap_top)/2)
    wire(direction, L_cap_bot, W_cap_bot)
    
    layername('aSi')
    extra_diel_x = 15.0
    extra_diel_y = 5.0
    wire(direction, L_cap_bot+2*extra_diel_y, W_cap_bot+2*extra_diel_x, shift=(-extra_diel_y,0))

    ## gap in NbTiN
    layername('NbTiN_GND')
    wire(direction, L_NBTIN_gap+12.0, W_NBTIN_gap, shift=(-gap_space, - (L_cap - W_cap)/2))
    
    ## Inductor attempt
    inductor_line = 3.0
    inductor_gap = 2.0
    large_gap = 9.0
    
    N = int(N_inductor);
    last_direction = -1
    L_ind = L_inductor
    
    movedirection(direction, L_cap_bot)
    movedirection(1, W_cap/2)
    setmark('lower_corner')
    
    ## start of inductor
    movedirection(-1,large_gap+1.5*inductor_line)
    layername('NbTiN_line')
    wire(-direction, (L_cap_bot-L_cap_top)/2, inductor_line)
    
    layername('aSi')
    wire(direction, 13.0, 13.0)
    
    layername('NbTiN_line')
    wirego(direction,19,inductor_line)
     
    layername('PPC_KID')
    movedirection(-direction, 12)
    
    
    wirego(direction,14,inductor_line+2.0)
    
    
    gomark('lower_corner')
    movedirection(-1,inductor_line/2)
    layername('PPC_KID')
    wirego(direction, 26, inductor_line )
    movedirection(direction,inductor_line/2)
    movedirection(1,inductor_line/2)
    wirego(-1,11,inductor_line)

    ## CPW like inductor
    inductor_base = parts.CPWs.CPW(inductor_gap, inductor_line, 36, 10, 'PPC_KID')
    movedirection(-direction, inductor_gap/2 + inductor_line/2)
    inductor_base.wirego(-1,L_ind-3)
    

    
    for nx in range(1,N):
        direction_out = inductor_base.square_turn_180_go(last_direction,-1j)
        inductor_base.wirego(direction_out,L_ind)
        last_direction = direction_out
        
    inductor_base.wirego(last_direction, inductor_line*2 + inductor_gap)
    wire(-last_direction,inductor_line,inductor_gap)

    return connectors
    

    
    