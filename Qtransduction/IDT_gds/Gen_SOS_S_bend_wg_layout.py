import numpy as np
from math import pi
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.resonator import RingResonator
from gdshelpers.layout import GridLayout
from gdshelpers.parts.marker import CrossMarker
from gdshelpers.parts.marker import SquareMarker
from gdshelpers.helpers.positive_resist import convert_to_positive_resist
from gdshelpers.parts.port import Port
from shapely.geometry import Polygon
from shapely.affinity import scale
from shapely.affinity import translate
from shapely.affinity import rotate
from gdshelpers.geometry import geometric_union
from gdshelpers.helpers.under_etching import create_holes_for_under_etching
from gdshelpers.geometry.ebl_frame_generators import raith_marker_frame
from gdshelpers.parts.text import Text
from shapely.geometry import Point

from shapely.geometry.base import geom_factory
from shapely.geos import lgeos
from shapely.validation import make_valid

#import the make_things_functions
import os
import sys

sys.path.append(os.path.abspath(r"/Users/itungchen/Documents/GitHub/Layout_Design_py/"))

import make_chirp_fingers_pair
import make_sing_fingers_pair
import make_displaced_IDT_pair
import make_zno_pad
import make_EBL_markers
import make_acoustic_wg
import make_acoustic_Rings
import make_acoustic_MZI
import make_Optomechanic_Rings
import make_Optomechanic_Rings_bend_Input_acoustic
import make_SOS_Optomechanic_Rings_bend_Input_acoustic
import make_unedr_etch_holes_ORR

import fIDT_ITung_20220404
import make_phononic_crystals

def generate_device_cell( sweep1, sweep2, cell_name):

    y_displacement_for_IDT = -50
    #Make the IDT fingers
    """
    fingers_and_smallpads,\
    Big_pads, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y, \
    left_x_coord_TR = make_chirp_fingers_pair.make_chirp_fingers_pairs(figer_widths=1, number_of_pairs=sweep1, IDT_Aperature=sweep2,  prop_length = 200)
    """
    # Modified from for the BGaP OMR paper (before 2023-04-17): figer_widths=0.5017, number_of_pairs=80, IDT_Aperature=15, prop_length=200+160+300+200
    # New parameters for Si-on-sapphire substrates (2023-04-20): figer_widths=0.25, number_of_pairs=65, IDT_Aperature=100, prop_length=sweep1
    # Note on prop length, for rings the proplength needs to be longer add 500 instead of 300: 200+160+300 to ACWG_ONLY:200+160+300 RR:200+160+500 , MZI 200+160+200 , ORR_BENT = 200+160+300
    # Figer_width = 1/4 of acoustic wavelength
    
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=0.45, number_of_pairs=80,
                                                                       IDT_Aperature=15, prop_length= 200+300+100+50, y_displacement= y_displacement_for_IDT)
    # For 2.5 GHz IDT, 1/4 wavelength = 0.45 um

    # Make ZnO pads
    ZnO_pad_R, ZnO_pad_L = make_zno_pad.make_ZnO_pads(zno_pad_x_length=350,
                            right_top_small_pad_TL_X = right_top_small_pad_TL_X,
                            right_top_small_pad_TL_Y= right_top_small_pad_TL_Y,
                                        pad_width = 90+10,
                                        left_x_coord_TR =left_x_coord_TR)

    
    # Make Optomechanic RingRes bending inputs
    # To control if optical WG is included, modified the function inside "make_Optomechanic_Rings_bend_Input_acoustic"
    OM_Ring, op_wg_right, Aco_wg, delta_y, tapered_coord_right, tapered_coord_left, \
    acoustic_bent_radius, ac_bend_angle_rad, y0_bend, y0_og, ring_origin = make_SOS_Optomechanic_Rings_bend_Input_acoustic.make_Optomechanic_Ring_bend(init_width=15,
                                                                                             fin_width=1.2,
                                                                                             prop_length= sweep2 ,#200 - 5 + 300,
                                                                                             # For rings the proplength needs to be longer :500
                                                                                             tapered_length=100,
                                                                                             top_right_x=top_right_x - 15,
                                                                                             # -15 is to align the bent waveguide
                                                                                             y_mid_IDT=y_mid_IDT,
                                                                                             L_IDT_area=shift_2,
                                                                                             aco_Gap = sweep1,
                                                                                             op_Gap=0.07,
                                                                                             ring_radius = 50,
                                                                                             y_displacement= y_displacement_for_IDT)
   
    # Align the IDT and the acoustic waveguide
    # Right IDT
    IDT_1 = translate(IDT_1, xoff= tapered_coord_right[0] - top_right_x)
    IDT_1_bigpad = translate(IDT_1_bigpad, xoff= tapered_coord_right[0] - top_right_x)
    ZnO_pad_R = translate(ZnO_pad_R, xoff= tapered_coord_right[0] - top_right_x)

    # Left IDT
    IDT_2 = translate(IDT_2, xoff= tapered_coord_left[0] - left_x_coord_TR, yoff = tapered_coord_left[1] - y0_bend)
    IDT_2_bigpad = translate(IDT_2_bigpad, xoff= tapered_coord_left[0] - left_x_coord_TR, yoff = tapered_coord_left[1]- y0_bend)
    ZnO_pad_L = translate(ZnO_pad_L, xoff= tapered_coord_left[0] - left_x_coord_TR, yoff = tapered_coord_left[1]- y0_bend)


    #################################################################################################################
    ##########################################BELOW IS MAKING A SINGLE OR DOUBLE SIDE DEVICES.

    #Displace a single ZnO pad
    # ZnO_pad_L = translate(ZnO_pad_L, yoff= y_displacement_for_IDT)

    #Single side
    One_side_ZnO_under_pads = geometric_union([ZnO_pad_L, ZnO_pad_R, IDT_1_bigpad, IDT_2_bigpad])
    One_side_ZnO_under_pads = One_side_ZnO_under_pads.buffer(6)

    # toogle on/off the accomodate for bent acoustic waveguide
    accomodatae_for_bent_acoustic_wg = True
    if accomodatae_for_bent_acoustic_wg == True:
        """ACCOMMODATE FOR BENT ACOUSTIC WG, COMMENT OUT IF NOT USING BENT AC WG"""
        bent_radius = acoustic_bent_radius
        y_delta_by_bending = bent_radius*(1-np.cos(ac_bend_angle_rad))

        shift_ring1 = y0_bend- y0_og
        shift_ring2 = y0_og - y_mid_IDT

        OM_Ring = translate(OM_Ring, yoff = -shift_ring1 + 5.3 - 0.55) #0.55 is a arbitrary number to shift the ring
    
    y_delta_by_bending = 0
    """ACCOMODATE END"""
    
    # Add name to cell
    text = Text(origin=[ top_right_x - sweep2, -65], height=20, text=str(cell_name), alignment='left-bottom')

    "-------------------------------Add Cells------------------------------------------"

    cell = Cell('SIMPLE_RES_DEVICE r={:.4f} g={:.4f}'.format(sweep1, sweep2))

    #cell.add_to_layer(1, No_WG_TOT, text)
    #cell.add_to_layer(1, cross_array, text)
    #cell.add_to_layer(1, convert_to_positive_resist(Aco, buffer_radius=10), text)

    """Single side fingers/pads/znos, Change Aco_RR to Aco_wg_only to get only WGs OR Aco_MZI"""
    # cell.add_to_layer(1, convert_to_positive_resist(Aco, buffer_radius=10), text)
    cell.add_to_layer(1, convert_to_positive_resist( [OM_Ring],  buffer_radius=10), text)
    cell.add_to_layer(2, One_side_ZnO_under_pads)
    cell.add_to_layer(3, IDT_1, IDT_2)
    cell.add_to_layer(4, IDT_1_bigpad, IDT_2_bigpad)
    

    """Two sides Aco WG/Racetracks/"""
    #cell.add_to_layer(1, convert_to_positive_resist(Aco, buffer_radius=10), text)
    #cell.add_to_layer(2, Two_side_ZnO_under_pad_and_fingers)
    #cell.add_to_layer(3, Two_side_sing_fingers_and_small_pads)
    #cell.add_to_layer(4, Two_side_Big_pads)
    

    """Two sides OM Wg and racetracks"""
    #cell.add_to_layer(1, convert_to_positive_resist( [OM_Ring],  buffer_radius=10), text)
    #cell.add_to_layer(2, Two_side_ZnO_under_pad_and_fingers)
    #cell.add_to_layer(3, Two_side_sing_fingers_and_small_pads)
    #cell.add_to_layer(4, Two_side_Big_pads)

    #Add the etch vias
    #cell.add_to_layer(5, holes_ring ,holes_idt )
    #cell.add_to_layer(5, holes_ring)

    #cell.add_to_layer(5, left_coupler)

    #cell.add_ebl_marker(layer=1, marker=CrossMarker(origin=(-500,-300 ), cross_length=10 , cross_width=5, paddle_length=5, paddle_width=5))

    "-------------------------------End of Add Cells------------------------------------------"

    return cell

if __name__ == "__main__":

    # Set the layout size
    layout_size = (12000, 10000)

    #Parameters wanted to scan-------------------------------------------
    #1550nm (best performance max_duty=0.80 grating_pitch=0.76)
    maximum_duty = np.linspace(0.75, 0.82, num = 2)
    grating_pitch = np.linspace(0.75, 0.77, num= 2)
    step =12
    """
    The best params are IDT fingers pair 65 pairs, aperature = 90um
    #number_of_finger_pairs = np.linspace(30, 90, num= int( (90-30) / step ) +1)
    #IDT_Aperatures = np.linspace(50, 200, num=6)
    """
    number_of_finger_pairs = [ 55, 60, 65]
    IDT_Aperatures = [ 80,  90, 95]
    #Acoustic waveguide parameters
    initial_acoustic_width = [5, 10, 15, 30]
    final_acoustic_width = [3]
    propagation_lengths = [250, 650, 950, 1400, 2000, 3020, 4300, 5500] #Delayline np.array(propagation_lengths) + 65
    acoustic_rr_gap = [0.07, 0.085, 0.1, 0.2, 0.5, 1, 50, 55]
    upperlength = [0, 8.5, 10.2, 13.6, 85, 102, 136 ]
    g11_gap = [0.07, 0.10, 0.14, 0.20]
    Ring_radius = [25, 30, 35, 40, 45]
    dummy = [1]

    # Change the sweep parameters here
    Parameters_scan_1 = acoustic_rr_gap
    Parameters_scan_2 =  propagation_lengths
    scan1_name = 'RR_gap'
    scan2_name = 'Prop_lengths'
    layout_name = 'Gen_SOS_S_bend_wg_layout_v3'
    

    #--------------------------------------------------------------------
    print('Scan1 =', Parameters_scan_1)
    print('Scan2 =', Parameters_scan_2)
    print('layout name = ', layout_name)

    layout = GridLayout(title=layout_name, frame_layer=0, text_layer=3, region_layer_type=None,
                        horizontal_spacing= -25, vertical_spacing= -75)

    #--------------------------------------------------------------------
    total = len(Parameters_scan_1) * len(Parameters_scan_2)
    count = 0
    #--------------------------------------------------------------------
    #Get input from user to see if they want show or save
    answer = input('Show or Save Layout?\n Input (save/show):')

    if answer == 'show':
        show = True
    if answer == 'save':
        show = False
    else:
        show = True

    #--------------------------------------------------------------------
    #Show or save running procedure
    if show == True:

        # Add column labels
        layout.add_column_label_row(( scan1_name +'= %0.2f' % 0.1 ), row_label='')
        layout.add_to_row(generate_device_cell(  sweep1 = Parameters_scan_1[0], sweep2 = Parameters_scan_2[0], cell_name = '1' ))
        layout_cell, mapping = layout.generate_layout()
        layout_cell.show()

    if show == False:
        #Start looping over the scanned parameters
        #Add column labels
        layout.add_column_label_row(( scan2_name +'= %0.2f' % param_2 for param_2 in Parameters_scan_2), row_label='')

        for param_1 in Parameters_scan_1:
            layout.begin_new_row(scan1_name+'=\n%0.2f' % param_1)
            for param_2 in Parameters_scan_2:
                count =  count + 1
                complete = count/total
                print("Number of cell generated / Total cell = %0.1f/%0.1f (%0.2f%% complete) " %(count ,total,complete*100) )
                layout.add_to_row(generate_device_cell( sweep1= param_1, sweep2=param_2, cell_name=count), alignment='center-center' , realign=True)

        layout_cell, mapping = layout.generate_layout()
        #layout_cell.add_ebl_frame(layer=1, size=40, frame_generator=raith_marker_frame, n=2)
        layout_cell.add_frame(frame_layer=1, line_width=1, bounds=(0,0,layout_size[0],layout_size[1]))

        # Show and then save the layout!
        make_EBL_markers.make_EBL_markers(layout_cell, delta_x=layout_size[0], delta_y=layout_size[1])
        print('saving........')
        layout_cell.show()
        layout_cell.save( layout_name + '.gds', grid_steps_per_micron=10000, parallel=True)
        print('saved!!!')