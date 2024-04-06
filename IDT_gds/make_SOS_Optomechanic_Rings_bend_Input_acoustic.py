import numpy as np
from math import pi
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.resonator import RingResonator
from gdshelpers.parts.splitter import Splitter
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

#import the make_things_functions
import os
import sys
sys.path.append(os.path.abspath(r"C:\Users\itong\Documents\GitHub\Layout_Design_py"))

# import make_Optomechanic_Rings_bend_optics

def make_Optomechanic_Ring_bend(init_width, fin_width, prop_length, tapered_length, top_right_x, y_mid_IDT, L_IDT_area,
                           aco_Gap, op_Gap, ring_radius, y_displacement ):
    phononicWG_initial_width = init_width
    phononicWG_fin_width = fin_width

    Gap = aco_Gap

    Wg_x_offset = 1.5 #um
    L_initial_width = L_IDT_area * 1.8
    race_length =0 #um
    vert_length = 0 #uw
    tapered_length = tapered_length
    ring_radius = ring_radius #um

    """Below parameter are simulated by Comsol and lumerical"""
    optical_wg_w = 1 #um
    optical_gap = op_Gap  # um #Gap FOR TE0 to TE0

    optical_coupling_length_TE0_TE0 = 50  # um

    TE2_WG_W = 0.25  # um
    TE2_TE0_Coupling_GaP = 0.2  # um #Gap FOR TE2 to TE0
    optical_coupling_length_TE2_TE0 = 60# um


    ac_coup_length = 30
    """"""
    """ADD STRAIGHT ACOUSTIC WAVEGUIDE 
          """

    ORR_RING = RingResonator(origin=(top_right_x-prop_length-tapered_length/2+20,0),
                             angle=0,
                             gap=-Gap,
                             width=phononicWG_fin_width,
                             radius=ring_radius,
                             vertical_race_length=vert_length,
                             race_length = race_length,
                             draw_opposite_side_wg=True,
                             straight_feeding=False)

    c_cord = ORR_RING.center_coordinates
    ring_x = c_cord[0]
    ring_y = c_cord[1]
    #Acoustic bending angle
    ac_bend_angle_rad = ac_coup_length * 0.5 / (ring_radius + phononicWG_fin_width + Gap)

    """ADD BENT ACOUSTIC WAVEGUIDE TOP"""
    # Making port from the ring and going out to the IDT
    Aco_wg_bent_top_right = Waveguide.make_at_port(
        Port((ring_x, ring_y + ring_radius + phononicWG_fin_width / 2 + Gap + phononicWG_fin_width / 2),
             angle=0,
             width=phononicWG_fin_width))
    Aco_wg_bent_top_right.add_bend(angle=-ac_bend_angle_rad, radius=ring_radius + phononicWG_fin_width + Gap)
    Aco_wg_bent_top_right.add_bend(angle=ac_bend_angle_rad, radius=10)
    Aco_wg_bent_top_right.add_bend(angle=np.pi / 2, radius=50)
    Aco_wg_bent_top_right.add_straight_segment(length=30) # The straight segment from the bend going out.
    Aco_wg_bent_top_right.add_bend(angle=-np.pi / 2, radius=50)
    Aco_wg_bent_top_right.add_straight_segment(length=(prop_length - 0.93 * L_initial_width - 40 - race_length) / 2 - ac_coup_length / 2)  # length of the final width
    Aco_wg_bent_top_right.add_straight_segment(length=tapered_length,
                                               final_width=phononicWG_initial_width)  # Tapered part of the WG
    Aco_wg_bent_top_right.add_straight_segment(length=L_initial_width)  # length of the initial width

    Aco_wg_bent_top_left = Waveguide.make_at_port(Aco_wg_bent_top_right.in_port,
             angle=np.pi,
             width=phononicWG_fin_width)
    Aco_wg_bent_top_left.add_bend(angle=ac_bend_angle_rad, radius=ring_radius + phononicWG_fin_width + Gap)
    Aco_wg_bent_top_left.add_bend(angle=-ac_bend_angle_rad, radius=10)
    Aco_wg_bent_top_left.add_bend(angle=-np.pi / 2, radius=50)
    Aco_wg_bent_top_left.add_straight_segment(length=30)
    Aco_wg_bent_top_left.add_bend(angle=np.pi / 2, radius=50)
    Aco_wg_bent_top_left.add_straight_segment(length=(prop_length - 0.93 * L_initial_width - 40 - race_length) / 2 - ac_coup_length / 2)  # length of the final width
    Aco_wg_bent_top_left.add_straight_segment(length=tapered_length,
                                              final_width=phononicWG_initial_width)  # Tapered part of the WG
    Aco_wg_bent_top_left.add_straight_segment(length=L_initial_width)  # length of the initial width

    """ADD BENT ACOUSTIC WAVEGUIDE BOT"""
    Aco_wg_bent_bot_right = Waveguide.make_at_port(
        Port((ring_x, ring_y - (ring_radius + phononicWG_fin_width / 2 + Gap + phononicWG_fin_width / 2)),
             angle=0,
             width=phononicWG_fin_width))
    Aco_wg_bent_bot_right.add_bend(angle=ac_bend_angle_rad, radius=ring_radius + phononicWG_fin_width + Gap)
    Aco_wg_bent_bot_right.add_bend(angle=-ac_bend_angle_rad, radius=40)
    #Aco_wg_bent_bot_right.add_bend(angle= 0, radius = 50)
    Aco_wg_bent_bot_right.add_straight_segment(length=0)
    #Aco_wg_bent_bot_right.add_bend(angle=np.pi / 2, radius = 50)
    Aco_wg_bent_bot_right.add_straight_segment(length=(prop_length - 0.93 * L_initial_width - 40 - race_length) / 2 - ac_coup_length / 2)  # length of the final width
    Aco_wg_bent_bot_right.add_straight_segment(length=tapered_length,
                                               final_width=phononicWG_initial_width)  # Tapered part of the WG
    Aco_wg_bent_bot_right.add_straight_segment(length=L_initial_width)  # length of the initial width
    tapered_coord_right = Aco_wg_bent_bot_right.current_port.origin # get the x coordinate at the interface between the tapered and the initial part of the WG

    Aco_wg_bent_bot_left = Waveguide.make_at_port(
        Aco_wg_bent_bot_right.in_port,
             angle=np.pi,
             width=phononicWG_fin_width)
    Aco_wg_bent_bot_left.add_bend(angle=-ac_bend_angle_rad, radius=ring_radius + phononicWG_fin_width + Gap)
    Aco_wg_bent_bot_left.add_bend(angle=+ac_bend_angle_rad, radius=40)
    Aco_wg_bent_bot_left.add_straight_segment(length= 20 )
    Aco_wg_bent_bot_left.add_bend(angle=np.pi / 2, radius=50)
    Aco_wg_bent_bot_left.add_straight_segment(length= 20 )
    Aco_wg_bent_bot_left.add_bend(angle=-np.pi / 2, radius=50)
    Aco_wg_bent_bot_left.add_straight_segment(length=(300 - 0.93 * L_initial_width - 40 - race_length) / 2 - ac_coup_length / 2)  # length of the final width
    Aco_wg_bent_bot_left.add_straight_segment(length=tapered_length,
                                              final_width=phononicWG_initial_width)  # Tapered part of the WG
    tapered_coord_left = Aco_wg_bent_bot_left.current_port.origin # get the coordinate at the interface between the tapered and the initial part of the WG
    Aco_wg_bent_bot_left.add_straight_segment(length=L_initial_width)  # length of the initial width
    
    """Union of all acoustic waveguides"""
    Aco_wg_union = geometric_union([Aco_wg_bent_top_right, Aco_wg_bent_top_left,
                                  Aco_wg_bent_bot_right, Aco_wg_bent_bot_left])
    
    end_coord = 0

    point = Point(ring_x, ring_y)
    point = point.buffer(5)

    # Bent Acoustic WG
    acoustic_bent_radius = ring_radius + phononicWG_fin_width + Gap


    """ADD OPTICAL WAVEGUIDE AND GC TO THE OM RR"""
    #Make optical waveguide and GC away from the center
    op_bend_angle_rad_TE02TE0 = optical_coupling_length_TE0_TE0*0.5  / (ring_radius + optical_wg_w + optical_gap)
    op_bend_angle_rad_TE22TE0 = optical_coupling_length_TE2_TE0*0.5  / (ring_radius + optical_wg_w/2 + TE2_WG_W/2 + TE2_TE0_Coupling_GaP)


    # Make Waveguides and GC on the right TE0 mode coupler
    op_wg_TE0_in = Waveguide.make_at_port(
        Port((ring_x + ring_radius + optical_wg_w + optical_gap ,  ring_y),
             angle=np.pi/2,
             width=optical_wg_w))

    op_wg_TE0_in.add_bend( angle= op_bend_angle_rad_TE02TE0, radius= ring_radius + optical_wg_w + optical_gap)
    op_wg_TE0_in.add_bend(angle= -op_bend_angle_rad_TE02TE0, radius= 10)
    op_wg_TE0_in.add_bend(angle= -np.pi / 2, radius=20)
    op_wg_TE0_in.add_straight_segment(length=100)
    op_wg_TE0_in.add_bend(angle= np.pi / 4, radius=20)


    # Make Waveguides and GC on the right TE0 mode coupler
    op_wg_TE0_thr = Waveguide.make_at_port(op_wg_TE0_in.in_port,
             angle=-np.pi/2,
             width=optical_wg_w)
    op_wg_TE0_thr.add_bend(angle=-op_bend_angle_rad_TE02TE0, radius=ring_radius + optical_wg_w + optical_gap)
    op_wg_TE0_thr.add_bend(angle=op_bend_angle_rad_TE02TE0, radius=10)
    op_wg_TE0_thr.add_bend(angle=np.pi / 2, radius=20)
    op_wg_TE0_thr.add_straight_segment(length=100)
    op_wg_TE0_thr.add_bend(angle=-np.pi / 4 - np.pi/2, radius=20)


    #Add the TE2 on the left in waveguide
    op_wg_TE2_in = Waveguide.make_at_port(Port((ring_x - (ring_radius + race_length/2 + phononicWG_fin_width/2 + TE2_TE0_Coupling_GaP + TE2_WG_W/2 ), ring_y),
                                                     angle= np.pi/2, width=TE2_WG_W))
    op_wg_TE2_in.add_bend(angle= -op_bend_angle_rad_TE22TE0, radius=ring_radius + (TE2_WG_W/2 + phononicWG_fin_width/2 + TE2_TE0_Coupling_GaP))
    op_wg_TE2_in.add_bend(angle= op_bend_angle_rad_TE22TE0,  radius=10)
    op_wg_TE2_in.add_bend(angle=  np.pi / 2 , radius=20)
    op_wg_TE2_in.add_straight_segment(length=200)
    op_wg_TE2_in.add_bend(angle= np.pi / 4, radius=20)

    #Add TE2 out waveguide
    op_wg_TE2_thr = Waveguide.make_at_port(op_wg_TE2_in.in_port,
                                               angle=-np.pi / 2,
                                           width=TE2_WG_W)
    op_wg_TE2_thr.add_bend(angle=op_bend_angle_rad_TE22TE0,
                          radius=ring_radius + (TE2_WG_W / 2 + phononicWG_fin_width / 2 + TE2_TE0_Coupling_GaP))
    op_wg_TE2_thr.add_bend(angle=-op_bend_angle_rad_TE22TE0, radius=10)
    op_wg_TE2_thr.add_bend(angle= -np.pi / 2, radius=20)
    op_wg_TE2_thr.add_straight_segment(length=100)
    op_wg_TE2_thr.add_bend(angle=-np.pi / 4 - np.pi / 2, radius=20)

#BGaP suspended paramters
    # Input TE0 waveguide 
    """coupler_params_TE5 = {
        'width': 1.01,
        'full_opening_angle': np.deg2rad(30),  # 40
        'grating_period': 0.690,
        'grating_ff': 0.79,  # minigap = 30nm
        'ap_max_ff': 0.835,
        'n_gratings': 20,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 20,  # 20
    }
    # Output TE2 waveguide 
    coupler_params_TE0 = {
        'width': 0.5,
        'full_opening_angle': np.deg2rad(30),  # 40
        'grating_period': 0.690,
        'grating_ff': 0.79,  # minigap = 30nm
        'ap_max_ff': 0.835,
        'n_gratings': 20,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 20,  # 20
    }
"""
    
# 220nm SOI suspended grating coupler
#Input TE0 waveguide
    IN_coupler_params_TE0 = {
        'width': 1.0,
        'full_opening_angle': np.deg2rad(30),  # 40
        'grating_period': 0.640,
        'grating_ff': 0.85,  # minigap = 30nm
        'ap_max_ff': 0.88,
        'n_gratings': 20,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 20,  # 20
    }
    OUT_coupler_params_TE2 = {
        'width': 0.25,
        'full_opening_angle': np.deg2rad(30),  # 40
        'grating_period': 0.640,
        'grating_ff': 0.85,  # minigap = 30nm
        'ap_max_ff': 0.88,
        'n_gratings': 20,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 20,  # 20
    }

    
    R_in_TE0_coupler = GratingCoupler.make_traditional_coupler_at_port(op_wg_TE0_in.current_port, **IN_coupler_params_TE0)
    R_in_TE2_coupler = GratingCoupler.make_traditional_coupler_at_port(op_wg_TE2_in.current_port, **OUT_coupler_params_TE2)
    R_thr_TE0_coupler = GratingCoupler.make_traditional_coupler_at_port(op_wg_TE0_thr.current_port, **IN_coupler_params_TE0)
    R_thr_TE2_coupler = GratingCoupler.make_traditional_coupler_at_port(op_wg_TE2_thr.current_port, **OUT_coupler_params_TE2)

    op_wg = geometric_union([ op_wg_TE0_in, op_wg_TE0_thr,
                             op_wg_TE2_in, op_wg_TE2_thr,
                              R_in_TE0_coupler,  R_thr_TE0_coupler,
                              R_in_TE2_coupler, R_thr_TE2_coupler])

    # Add op_wg and Aco_wg_union to the geometric_union of the OMR_total to have optical/acoustic WG at the layout.
    Aco_wg = geometric_union([Aco_wg_bent_bot_right, Aco_wg_bent_bot_left])
    if Gap > 5:
        OMR_total = geometric_union([Aco_wg])
    else:
        OMR_total = geometric_union([ORR_RING, Aco_wg])
    
    #op_wg_right_in, op_wg_right_thr,
    y1 = Aco_wg_bent_top_right.y
    y0_bend = Aco_wg_bent_bot_right.y
    y0_og =0
    delta_y = y1-y0_bend
    ring_origin = ORR_RING.center_coordinates
   
    return OMR_total, op_wg, Aco_wg, delta_y, tapered_coord_right, tapered_coord_left, acoustic_bent_radius, ac_bend_angle_rad, y0_bend, y0_og, ring_origin