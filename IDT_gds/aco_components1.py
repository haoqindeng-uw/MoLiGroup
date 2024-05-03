import numpy as np
import math
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

# Import help functions written by I-Tung
import importlib
import make_displaced_IDT_pair
importlib.reload(make_displaced_IDT_pair)
import make_zno_pad
importlib.reload(make_zno_pad)
import make_SOS_Optomechanic_Rings_bend_Input_acoustic
importlib.reload(make_SOS_Optomechanic_Rings_bend_Input_acoustic)

def make_dosetest_IDT(cell: Cell, prop_len=200, wg_width=1.2, finger_width=0.445, number_of_pairs=80, IDT_Aperature=15, 
                               translation_offset=[0,0], guided=True):
    # print('debug pos: ', translation_offset)
    # print('debug IDT aperture: ', IDT_Aperature)
    y_displacement_for_IDT = 0
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR, port_coordinates = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=finger_width, number_of_pairs=number_of_pairs,
                                                                        IDT_Aperature=IDT_Aperature, prop_length= 200+300+100+50+prop_len, y_displacement= y_displacement_for_IDT)
    
    x_off = translation_offset[0]
    y_off = translation_offset[1]
    IDT_layer = geometric_union([IDT_1])
    IDT_pad_layer = geometric_union([IDT_1_bigpad])
    IDT_layer = translate(IDT_layer, xoff=x_off, yoff=y_off)
    IDT_pad_layer = translate(IDT_pad_layer, xoff=x_off, yoff=y_off)
    # print('debug pos: ', [x_off, y_off])

    # cell.add_to_layer(1, IDT_pad_layer)
    cell.add_to_layer(1, IDT_layer)
    return cell

def make_single_IDT(cell: Cell, prop_len=200, wg_width=1.2, finger_width=0.45, number_of_pairs=80, IDT_Aperature=15, 
                               translation_offset=[0,0], guided=True):
    # print('debug pos: ', translation_offset)
    # print('debug IDT aperture: ', IDT_Aperature)
    y_displacement_for_IDT = 0
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR, port_coordinates = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=finger_width, number_of_pairs=number_of_pairs,
                                                                        IDT_Aperature=IDT_Aperature, prop_length= 200+300+100+50+prop_len, y_displacement= y_displacement_for_IDT)
    
    x_off = translation_offset[0]
    y_off = translation_offset[1]
    IDT_layer = geometric_union([IDT_1, IDT_1_bigpad])
    IDT_pad_layer = geometric_union([IDT_1_bigpad])
    IDT_layer = translate(IDT_layer, xoff=x_off, yoff=y_off)
    IDT_pad_layer = translate(IDT_pad_layer, xoff=x_off, yoff=y_off)
    # print('debug pos: ', [x_off, y_off])

    # cell.add_to_layer(1, IDT_pad_layer)
    cell.add_to_layer(1, IDT_layer)
    return cell

def make_aco_tapered_stright_delayline(cell: Cell, prop_len=200, wg_width=1.2, finger_width=0.45, number_of_pairs=80, IDT_Aperature=15, 
                               translation_offset=[0,0], guided=True):
    y_displacement_for_IDT = 0
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR, port_coordinates = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=finger_width, number_of_pairs=number_of_pairs,
                                                                        IDT_Aperature=IDT_Aperature, prop_length= 200+300+100+50+prop_len, y_displacement= y_displacement_for_IDT)
    
    wg_right_org_x = top_right_x
    wg_right_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_right_width = IDT_Aperature + 5
    wg_right_len = 172.8

    wg_left_org_x = -751.6 - prop_len
    wg_left_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_left_width = IDT_Aperature + 5
    wg_left_len = 172.8

    wg_taper_width = wg_width
    wg_taper_len = 100

    print('origin left x: ', wg_left_org_x)
    print('origin right x: ', wg_right_org_x)

    wg_right = Waveguide.make_at_port(Port(origin=(wg_right_org_x, wg_right_org_y), angle=np.pi, width=wg_right_width))
    wg_right.add_straight_segment(length=wg_right_len)
    wg_right.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    taper_right_origin = wg_right.port.origin
    wg_right.add_straight_segment(prop_len + 200)

    wg_left = Waveguide.make_at_port(Port(origin=(wg_left_org_x, wg_left_org_y), angle=0, width=wg_left_width))
    wg_left.add_straight_segment(length=wg_left_len)
    wg_left.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    taper_right_origin = wg_left.port.origin
    wg_left.add_straight_segment(prop_len + 200)

    # draw w

    IDT_layer = geometric_union([IDT_1, IDT_2])
    IDT_pad_layer = geometric_union([IDT_1_bigpad, IDT_2_bigpad])
    aco_wg_layer = geometric_union([wg_left, wg_right])

    # Make ZnO pads
    ZnO_pad_R, ZnO_pad_L = make_zno_pad.make_ZnO_pads(zno_pad_x_length=350,
                            right_top_small_pad_TL_X = right_top_small_pad_TL_X,
                            right_top_small_pad_TL_Y= right_top_small_pad_TL_Y,
                                        pad_width = 90+10,
                                        left_x_coord_TR =left_x_coord_TR)
    # ZnO pads (with buffer)
    One_side_ZnO_under_pads = geometric_union([ZnO_pad_L, ZnO_pad_R, IDT_1_bigpad, IDT_2_bigpad])
    One_side_ZnO_under_pads = One_side_ZnO_under_pads.buffer(6)

    x_off = translation_offset[0]
    y_off = translation_offset[1]
    aco_wg_layer = translate(aco_wg_layer, xoff=x_off, yoff=y_off)
    IDT_layer = translate(IDT_layer, xoff=x_off, yoff=y_off)
    IDT_pad_layer = translate(IDT_pad_layer, xoff=x_off, yoff=y_off)
    One_side_ZnO_under_pads = translate(One_side_ZnO_under_pads, xoff=x_off, yoff=y_off)
    
    if guided is True:
        cell.add_to_layer(1, convert_to_positive_resist( [aco_wg_layer],  buffer_radius=10))
    cell.add_to_layer(4, IDT_pad_layer)
    cell.add_to_layer(3, IDT_layer)
    cell.add_to_layer(2, One_side_ZnO_under_pads)

    return cell

def make_IDT_stright_delayline(cell: Cell, prop_len=200, wg_width=1.2, finger_width=0.45, number_of_pairs=80, IDT_Aperature=15, 
                               translation_offset=[0,0], guided=True):
    y_displacement_for_IDT = 0
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR, port_coordinates = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=finger_width, number_of_pairs=number_of_pairs,
                                                                        IDT_Aperature=IDT_Aperature, prop_length= 200+300+100+50+prop_len, y_displacement= y_displacement_for_IDT)
    print('hello')
    print(top_right_x, left_x_coord_TR, left_y_coord_TR, port_coordinates)

    print(port_coordinates[0][0][0])
    print(port_coordinates[2][0][0])
    wg_right_org_x = top_right_x

    wg_right_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_right_width = IDT_Aperature + 5
    wg_right_len = 172.8 + 50 + 1.2
    wg_right_len = 205
    wg_right_org_x = port_coordinates[2][0][0] + wg_right_len

    wg_left_org_x = -751.6 - prop_len

    
    wg_left_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_left_width = IDT_Aperature + 5
    wg_left_len = 172.8 + 30 + 1.2
    wg_left_len = 205
    wg_left_org_x = port_coordinates[0][0][0] - wg_left_len

    wg_taper_width = wg_width
    wg_taper_len = 100

    wg_right = Waveguide.make_at_port(Port(origin=(wg_right_org_x, wg_right_org_y), angle=np.pi, width=wg_right_width))
    wg_right.add_straight_segment(length=wg_right_len)
    wg_right.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    wg_right.add_straight_segment(prop_len + 200+50)

    wg_left = Waveguide.make_at_port(Port(origin=(wg_left_org_x, wg_left_org_y), angle=0, width=wg_left_width))
    wg_left.add_straight_segment(length=wg_left_len)
    wg_left.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    wg_left.add_straight_segment(prop_len + 200+50)

    IDT_layer = geometric_union([IDT_1, IDT_2])
    IDT_pad_layer = geometric_union([IDT_1_bigpad, IDT_2_bigpad])
    aco_wg_layer = geometric_union([wg_left, wg_right])

    # Make ZnO pads
    ZnO_pad_R, ZnO_pad_L = make_zno_pad.make_ZnO_pads(zno_pad_x_length=350,
                            right_top_small_pad_TL_X = right_top_small_pad_TL_X,
                            right_top_small_pad_TL_Y= right_top_small_pad_TL_Y,
                                        pad_width = 90+10,
                                        left_x_coord_TR =left_x_coord_TR)
    # ZnO pads (with buffer)
    One_side_ZnO_under_pads = geometric_union([ZnO_pad_L, ZnO_pad_R, IDT_1_bigpad, IDT_2_bigpad])
    One_side_ZnO_under_pads = One_side_ZnO_under_pads.buffer(6)

    x_off = translation_offset[0]
    y_off = translation_offset[1]
    aco_wg_layer = translate(aco_wg_layer, xoff=x_off, yoff=y_off)
    IDT_layer = translate(IDT_layer, xoff=x_off, yoff=y_off)
    IDT_pad_layer = translate(IDT_pad_layer, xoff=x_off, yoff=y_off)
    One_side_ZnO_under_pads = translate(One_side_ZnO_under_pads, xoff=x_off, yoff=y_off)
    
    if guided is True:
        cell.add_to_layer(1, convert_to_positive_resist( [aco_wg_layer],  buffer_radius=10))
    cell.add_to_layer(4, IDT_pad_layer)
    cell.add_to_layer(3, IDT_layer)
    cell.add_to_layer(2, One_side_ZnO_under_pads)

    return cell

def make_OMR(cell: Cell, prop_len=200, wg_width=1.2, finger_width=0.45, number_of_pairs=80, IDT_Aperature=15, 
                               translation_offset=[0,0], guided=True, aco_gap = 0.2, te0_width=1.2, te2_width=0.39, 
                               racetrack_width=1.2, racetrack_len=100, racetrack_r = 50, te0_gap = 0.1):
    y_displacement_for_IDT = 0
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR, port_coordinates = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=finger_width, number_of_pairs=number_of_pairs,
                                                                        IDT_Aperature=IDT_Aperature, prop_length= 200+300+100+50+prop_len, y_displacement= y_displacement_for_IDT)
    # print('hello')
    # print(top_right_x, left_x_coord_TR, left_y_coord_TR, port_coordinates)

    # print(port_coordinates[0][0][0])
    # print(port_coordinates[2][0][0])
    wg_right_org_x = top_right_x

    wg_right_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_right_width = IDT_Aperature + 5
    wg_right_len = 172.8 + 50 + 1.2
    wg_right_len = 205
    wg_right_org_x = port_coordinates[2][0][0] + wg_right_len

    wg_left_org_x = -751.6 - prop_len

    
    wg_left_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_left_width = IDT_Aperature + 5
    wg_left_len = 172.8 + 30 + 1.2
    wg_left_len = 205
    wg_left_org_x = port_coordinates[0][0][0] - wg_left_len

    wg_taper_width = wg_width
    wg_taper_len = 100

    wg_right = Waveguide.make_at_port(Port(origin=(wg_right_org_x, wg_right_org_y), angle=np.pi, width=wg_right_width))
    wg_right.add_straight_segment(length=wg_right_len)
    wg_right.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    wg_right.add_straight_segment(prop_len + 200+50)

    wg_left = Waveguide.make_at_port(Port(origin=(wg_left_org_x, wg_left_org_y), angle=0, width=wg_left_width))
    wg_left.add_straight_segment(length=wg_left_len)
    wg_left.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    wg_left.add_straight_segment(prop_len + 200+50)

    IDT_layer = geometric_union([IDT_1, IDT_2])
    IDT_pad_layer = geometric_union([IDT_1_bigpad, IDT_2_bigpad])
    aco_wg_layer = geometric_union([wg_left, wg_right])

    # Make ZnO pads
    ZnO_pad_R, ZnO_pad_L = make_zno_pad.make_ZnO_pads(zno_pad_x_length=350,
                            right_top_small_pad_TL_X = right_top_small_pad_TL_X,
                            right_top_small_pad_TL_Y= right_top_small_pad_TL_Y,
                                        pad_width = 90+10,
                                        left_x_coord_TR =left_x_coord_TR)
    # ZnO pads (with buffer)
    One_side_ZnO_under_pads = geometric_union([ZnO_pad_L, ZnO_pad_R, IDT_1_bigpad, IDT_2_bigpad])
    One_side_ZnO_under_pads = One_side_ZnO_under_pads.buffer(6)

    x_off = translation_offset[0]
    y_off = translation_offset[1]
    aco_wg_layer = translate(aco_wg_layer, xoff=x_off, yoff=y_off)
    IDT_layer = translate(IDT_layer, xoff=x_off, yoff=y_off)
    IDT_pad_layer = translate(IDT_pad_layer, xoff=x_off, yoff=y_off)
    One_side_ZnO_under_pads = translate(One_side_ZnO_under_pads, xoff=x_off, yoff=y_off)
    


    # make racetrack ring
    ring_org_x = (wg_left_org_x + wg_right_org_x) / 2
    ring_org_y = wg_left_org_y + racetrack_width + aco_gap

    ring = Waveguide.make_at_port(Port(origin=(ring_org_x, ring_org_y), angle=0, width=racetrack_width))
    ring.add_straight_segment(length=racetrack_len / 2)
    # ring.add_bend(radius=50, angle=np.pi * 2 / 3)
    # ring.add_straight_segment(length=racetrack_len)
    # ring.add_bend(radius=50, angle=np.pi * 2 / 3)
    # ring.add_straight_segment(length=racetrack_len)
    # ring.add_bend(radius=50, angle=np.pi * 2 / 3)
    # ring.add_straight_segment(length=racetrack_len / 2)
    # ring.add_straight_segment(length=racetrack_len / 2)
    # ring.add_bend(radius=50, angle=np.pi)
    # ring.add_straight_segment(length=racetrack_len / 2)
    # pos = ring.origin
    # ring.add_straight_segment(length=racetrack_len / 2)
    # ring.add_bend(radius=50, angle=np.pi)
    # ring.add_straight_segment(length=racetrack_len / 2)
    # te0_wg_org_x = pos[0]
    # te0_wg_org_y = pos[1] + racetrack_gap + te0_width / 2 + racetrack_width / 2
    # te0_wg =  Waveguide.make_at_port(Port(origin=(te0_wg_org_x, te0_wg_org_y), angle=0, width=te0_width))
    # te0_wg.add_straight_segment(length=450)
    # te0_wg.add_bend(radius=50, angle=np.pi/2)
    # cell.add_to_layer(4, IDT_pad_layer)
    # cell.add_to_layer(3, IDT_layer)
    # cell.add_to_layer(2, One_side_ZnO_under_pads)

    # if guided is True:
    #     cell.add_to_layer(1, convert_to_positive_resist( [aco_wg_layer, ring, te0_wg],  buffer_radius=10))


    ring.add_bend(radius=50, angle=np.pi * 2 / 3)
    ring.add_straight_segment(length=racetrack_len)
    ring.add_bend(radius=50, angle=np.pi * 2 / 3)
    ring.add_straight_segment(length=racetrack_len / 2)
    te0_pos = ring.origin
    print('debug pos')
    print(te0_pos)
    print(math.sin(np.pi/3))
    te0_org_x = te0_pos[0] - (te0_gap + racetrack_width/2 + te0_width/2) * math.sin(np.pi/3)
    te0_org_y = te0_pos[1] + (te0_gap + racetrack_width/2 + te0_width/2) * math.cos(np.pi/3)
    # te0_org = (te0_pos[0] + (te0_gap + racetrack_width/2 + te0_width/2) * math.cos(np.pi/3), te0_pos[1] + (te0_gap + racetrack_width/2 + te0_width/2) * math.sin(np.pi/3))
    te0_wg = Waveguide.make_at_port(Port(origin=(te0_org_x, te0_org_y), angle=np.pi/3, width=te0_width))
    te0_wg.add_straight_segment(length=100)
    
    ring.add_straight_segment(length=racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi * 2 / 3)
    ring.add_straight_segment(length=racetrack_len / 2)

    cell.add_to_layer(4, IDT_pad_layer)
    cell.add_to_layer(3, IDT_layer)
    cell.add_to_layer(2, One_side_ZnO_under_pads)

    if guided is True:
        cell.add_to_layer(1, convert_to_positive_resist( [aco_wg_layer, ring, te0_wg],  buffer_radius=10))

    return cell


def make_aco_directional_coupler(cell: Cell, prop_len=200, radius=250, y_displacement=150, wg_width=1.2, finger_width=0.45, number_of_pairs=80, 
                            IDT_Aperature=15, coupling_len=50, arc_len_level=1,
                            translation_offset=[0,0], guided=True, total_prop_len=700):
    total_straight_len = 0
    y_displacement_for_IDT = 0
    IDT_1, IDT_1_bigpad, \
    IDT_2, IDT_2_bigpad, \
    top_right_x, y_mid_IDT, shift_2, \
    right_top_small_pad_TL_X, right_top_small_pad_TL_Y,\
    left_x_coord_TR, left_y_coord_TR, port_coordinates = make_displaced_IDT_pair.make_displaced_IDT_pairs(figer_widths=finger_width, number_of_pairs=number_of_pairs,
                                                                        IDT_Aperature=IDT_Aperature, prop_length= 200+300+100+50+prop_len, y_displacement= y_displacement_for_IDT)
    
    wg_right_org_x = top_right_x
    wg_right_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2 + y_displacement
    wg_right_width = IDT_Aperature
    wg_right_len = 172.8

    wg_left_org_x = -751.6 - prop_len
    wg_left_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2
    wg_left_width = IDT_Aperature
    wg_left_len = 172.8

    wg_down_right_org_x = top_right_x
    wg_down_right_org_y = (port_coordinates[0][1][1] + port_coordinates[1][1][1]) / 2 - y_displacement
    wg_down_right_width = 15
    wg_down_right_len = 172.8

    wg_taper_width = wg_width
    wg_taper_len = 100

    # arc_len_level = 1
    arc_len = 50 * np.pi * 1/5 * arc_len_level
    alpha = arc_len / radius
    # radius = 250
    # alpha = np.pi/4

    wg_right = Waveguide.make_at_port(Port(origin=(wg_right_org_x, wg_right_org_y), angle=np.pi, width=wg_right_width))
    wg_right.add_straight_segment(length=wg_right_len)
    wg_right.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    wg_right_org = wg_right.port.origin
    # wg_right.add_straight_segment(40)

    wg_down_right = Waveguide.make_at_port(Port(origin=(wg_down_right_org_x, wg_down_right_org_y), angle=np.pi, width=wg_down_right_width))
    wg_down_right.add_straight_segment(length=wg_down_right_len)
    wg_down_right.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    # wg_down_right.add_straight_segment(40)

    wg_left = Waveguide.make_at_port(Port(origin=(wg_left_org_x, wg_left_org_y), angle=0, width=wg_left_width))
    wg_left.add_straight_segment(length=wg_left_len)
    wg_left.add_straight_segment(length=wg_taper_len, final_width=wg_taper_width)
    wg_left.add_straight_segment(100)
    total_straight_len += 100

    ### needs modifying
    gap = 0.1
    wg_down_port = (wg_left.port.origin[0], wg_left.port.origin[1] - wg_taper_width - gap)
    wg_left.add_straight_segment(coupling_len)
    total_straight_len += coupling_len

    print('wg down port: ', wg_down_port)
    wg_down = Waveguide.make_at_port(Port(origin=wg_down_port, angle=0, width=wg_taper_width))
    wg_down.add_straight_segment(length=coupling_len)
    wg_down.add_arc(final_angle=(-alpha), radius=radius)
    print('wg_down: ')
    print('alpha: ', alpha / np.pi, 'pi')
    print('radius:', radius)
    len_c = (y_displacement - wg_taper_width - gap - (radius - radius * math.cos(alpha)) * 2) / math.sin(alpha)
    print(y_displacement - wg_taper_width - gap)
    print(radius - radius * math.cos(alpha))
    print(math.sin(alpha))
    print('len_c: ', len_c)

    wg_down.add_straight_segment(length=len_c)
    wg_down.add_arc(final_angle=(0), radius=radius)
    len_remain = wg_down_right.port.origin[0] - wg_down.port.origin[0]
    wg_down.add_straight_segment(len_remain)

    print('wg down port: ', wg_down_port)
    wg_down2 = Waveguide.make_at_port(Port(origin=wg_down_port, angle=(-np.pi), width=wg_taper_width))
    wg_down2.add_arc(final_angle=(-np.pi*3/4), radius=radius/4)
    # wg_down2.add_arc(final_angle=(-(np.pi - alpha)), radius=radius/3)
    wg_down2.add_straight_segment(length=20)
    wg_down2.add_straight_segment(length=20, final_width=0.001)

    len_c = (y_displacement - (radius - radius * math.cos(alpha)) * 2) / math.sin(alpha)
    # len_c = 100


    wg_left.add_arc(final_angle=(alpha), radius=radius)
    print('wg_left: ')
    print(alpha)
    print(radius)
    wg_left.add_straight_segment(length=len_c)
    wg_left.add_arc(final_angle=(0), radius=radius)
    # wg_left.add_straight_segment(160)

    total_straight_len += len_c

    print('total_len1: ', total_straight_len)
    len_remain = total_prop_len - total_straight_len
    len_remain = wg_right.port.origin[0] - wg_left.port.origin[0]
    wg_left.add_straight_segment(length=len_remain)

    total_straight_len += len_remain
    print('total_straight_len: ', total_straight_len)
    wg_left_org = wg_left.port.origin
    print('port origins: ', wg_left_org, wg_right_org)

    IDT_layer = geometric_union([IDT_1, IDT_2])
    IDT_pad_layer = geometric_union([IDT_1_bigpad, IDT_2_bigpad])
    aco_wg_layer = geometric_union([wg_left, wg_right])
    ### needs modifying

    IDT_3 = IDT_1
    IDT_1 = translate(IDT_1, yoff=y_displacement)
    IDT_3 = translate(IDT_3, yoff=(-y_displacement))

    IDT_3_bigpad = IDT_1_bigpad
    IDT_1_bigpad = translate(IDT_1_bigpad, yoff=y_displacement)
    IDT_3_bigpad = translate(IDT_3_bigpad, yoff=(-y_displacement))

    IDT_layer = geometric_union([IDT_1, IDT_2, IDT_3])
    IDT_pad_layer = geometric_union([IDT_1_bigpad, IDT_2_bigpad, IDT_3_bigpad])
    aco_wg_layer = geometric_union([wg_left, wg_right, wg_down, wg_down_right, wg_down2])

    # Make ZnO pads
    ZnO_pad_R, ZnO_pad_L = make_zno_pad.make_ZnO_pads(zno_pad_x_length=350,
                            right_top_small_pad_TL_X = right_top_small_pad_TL_X,
                            right_top_small_pad_TL_Y= right_top_small_pad_TL_Y,
                                        pad_width = 90+10,
                                        left_x_coord_TR =left_x_coord_TR)
    # ZnO pads (with buffer)
    ZnO_pad_R2 = ZnO_pad_R
    ZnO_pad_R = translate(ZnO_pad_R, yoff=y_displacement)
    ZnO_pad_R2 = translate(ZnO_pad_R2, yoff=-y_displacement)
    One_side_ZnO_under_pads = geometric_union([ZnO_pad_L, ZnO_pad_R, ZnO_pad_R2, IDT_1_bigpad, IDT_2_bigpad, IDT_3_bigpad])
    One_side_ZnO_under_pads = One_side_ZnO_under_pads.buffer(6)

    # x_off = translation_offset[0]
    # y_off = translation_offset[1]
    # aco_wg_layer = translate(aco_wg_layer, xoff=x_off, yoff=y_off)
    # IDT_layer = translate(IDT_layer, xoff=x_off, yoff=y_off)
    # IDT_pad_layer = translate(IDT_pad_layer, xoff=x_off, yoff=y_off)
    # One_side_ZnO_under_pads = translate(One_side_ZnO_under_pads, xoff=x_off, yoff=y_off)
    
    if guided is True:
        cell.add_to_layer(1, convert_to_positive_resist( [aco_wg_layer],  buffer_radius=10))
    cell.add_to_layer(4, IDT_pad_layer)
    cell.add_to_layer(3, IDT_layer) 
    cell.add_to_layer(2, One_side_ZnO_under_pads)

    return cell

def make_racetrack_ring(cell, te0_width=1.2, te2_width=0.39, racetrack_width=1.2, te0_gap=0.1, te2_gap=0.1, te0_coupling_len=100, te2_coupling_len=17,
                        racetrack_len = 200,
                        offset=(0,0)):
    '''
    te0 is upper wg,
    te2 is buttom wg.
    '''
    ring_org = offset
    ring = Waveguide.make_at_port(Port(origin=ring_org, angle=0, width=racetrack_width))
    ring.add_straight_segment(length = racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi)
    ring.add_straight_segment(length = racetrack_len / 2)
    pos = ring.origin
    ring.add_straight_segment(length = racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi)
    ring.add_straight_segment(length = racetrack_len / 2)   


    te0_org = (pos[0], pos[1] + (te0_width/2 + racetrack_width/2 + te0_gap))
    te0_wg_r = Waveguide.make_at_port(Port(origin=te0_org, angle=0, width=te0_width))
    te0_wg_r.add_straight_segment(length=te0_coupling_len/2)
    te0_wg_r.add_bend(radius=40, angle=np.pi/4)
    te0_wg_r.add_bend(radius=40, angle=-np.pi/4)
    te0_wg_r.add_straight_segment(length=offset[0] + 375 - te0_wg_r.origin[0] - 50)
    te0_wg_r.add_bend(radius=50, angle=-np.pi/2)
    te0_wg_r.add_straight_segment(length=te0_wg_r.origin[1] - (-100 + offset[1]))
    te0_wg_l = Waveguide.make_at_port(Port(origin=te0_org, angle=np.pi, width=te0_width))
    te0_wg_l.add_straight_segment(length=te0_coupling_len/2)
    te0_wg_l.add_bend(radius=40, angle=-np.pi/4)
    te0_wg_l.add_bend(radius=40, angle=np.pi/4)
    te0_wg_l.add_straight_segment(length= te0_wg_l.origin[0] -(offset[0] - 375 + 50))
    te0_wg_l.add_bend(radius=50, angle=np.pi/2)
    te0_wg_l.add_straight_segment(length=te0_wg_l.origin[1] - (-100 + offset[1]))

    if te0_coupling_len <= 120:
        te2_org = (ring_org[0], ring_org[1] - (te2_width/2 + racetrack_width/2 + te2_gap))
        te2_wg_r = Waveguide.make_at_port(Port(origin=te2_org, angle=0, width=te2_width))
        te2_wg_r.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_r.add_bend(radius=25, angle=-np.pi/4)
        te2_wg_r.add_bend(radius=25, angle=np.pi/4)
        te2_wg_r.add_straight_segment(length=offset[0] + 125 - 25 - te2_wg_r.origin[0])
        te2_wg_r.add_bend(radius=25, angle=-np.pi/2)
        te2_wg_r.add_straight_segment(length=te2_wg_r.origin[1] - (-100 + offset[1]))


        te2_wg_l = Waveguide.make_at_port(Port(origin=te2_org, angle=np.pi, width=te2_width))
        te2_wg_l.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_l.add_bend(radius=25, angle=np.pi/4)
        te2_wg_l.add_bend(radius=25, angle=-np.pi/4)
        te2_wg_l.add_straight_segment(length=te2_wg_l.origin[0] - (offset[0] - 125 + 25) )
        te2_wg_l.add_bend(radius=25, angle=np.pi/2)
        te2_wg_l.add_straight_segment(length=te2_wg_l.origin[1] - (-100 + offset[1]))
    else:
        bending_radius = 125 - te2_coupling_len / 2
        te2_org = (ring_org[0], ring_org[1] - (te2_width/2 + racetrack_width/2 + te2_gap))
        te2_wg_r = Waveguide.make_at_port(Port(origin=te2_org, angle=0, width=te2_width))
        te2_wg_r.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_r.add_bend(radius=bending_radius, angle=-np.pi/2)
        te2_wg_r.add_straight_segment(length=te2_wg_r.origin[1] - (-100 + offset[1]))


        te2_wg_l = Waveguide.make_at_port(Port(origin=te2_org, angle=np.pi, width=te2_width))
        te2_wg_l.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_l.add_bend(radius=bending_radius, angle=np.pi/2)
        te2_wg_l.add_straight_segment(length=te2_wg_l.origin[1] - (-100 + offset[1]))

    coupler1_params = {
        'width': te0_width,
        'full_opening_angle': np.deg2rad(40),  # 40
        'grating_period': 0.7,
        'grating_ff': 0.85,  # minigap = 30nm
        # 'ap_max_ff':0.85,
        'ap_max_ff':0.99,
        'n_gratings': 20,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 20,  # 20
    }

    gc1 = GratingCoupler.make_traditional_coupler(origin=te0_wg_r.origin, **coupler1_params)
    gc2 = GratingCoupler.make_traditional_coupler(origin=te0_wg_l.origin, **coupler1_params)
    gc3 = GratingCoupler.make_traditional_coupler(origin=te2_wg_r.origin, **coupler1_params)
    gc4 = GratingCoupler.make_traditional_coupler(origin=te2_wg_l.origin, **coupler1_params)

    cell.add_to_layer(1, convert_to_positive_resist( [ring, te0_wg_r, te0_wg_l, te2_wg_r, te2_wg_l,
                                                    gc1, gc2, gc3, gc4],  buffer_radius=5))

    return cell

def make_racetrack_ring(cell, te0_width=1.2, te2_width=0.39, racetrack_width=1.2, te0_gap=0.1, te2_gap=0.1, te0_coupling_len=100, te2_coupling_len=17,
                        racetrack_len = 200,
                        offset=(0,0)):
    '''
    te0 is upper wg,
    te2 is buttom wg.
    '''
    ring_org = offset
    ring = Waveguide.make_at_port(Port(origin=ring_org, angle=0, width=racetrack_width))
    ring.add_straight_segment(length = racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi)
    ring.add_straight_segment(length = racetrack_len / 2)
    pos = ring.origin
    ring.add_straight_segment(length = racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi)
    ring.add_straight_segment(length = racetrack_len / 2)   


    te0_org = (pos[0], pos[1] + (te0_width/2 + racetrack_width/2 + te0_gap))
    te0_wg_r = Waveguide.make_at_port(Port(origin=te0_org, angle=0, width=te0_width))
    te0_wg_r.add_straight_segment(length=te0_coupling_len/2)
    te0_wg_r.add_bend(radius=40, angle=np.pi/4)
    te0_wg_r.add_bend(radius=40, angle=-np.pi/4)
    te0_wg_r.add_straight_segment(length=offset[0] + 375 - te0_wg_r.origin[0] - 50)
    te0_wg_r.add_bend(radius=50, angle=-np.pi/2)
    te0_wg_r.add_straight_segment(length=te0_wg_r.origin[1] - (-100 + offset[1]))
    te0_wg_l = Waveguide.make_at_port(Port(origin=te0_org, angle=np.pi, width=te0_width))
    te0_wg_l.add_straight_segment(length=te0_coupling_len/2)
    te0_wg_l.add_bend(radius=40, angle=-np.pi/4)
    te0_wg_l.add_bend(radius=40, angle=np.pi/4)
    te0_wg_l.add_straight_segment(length= te0_wg_l.origin[0] -(offset[0] - 375 + 50))
    te0_wg_l.add_bend(radius=50, angle=np.pi/2)
    te0_wg_l.add_straight_segment(length=te0_wg_l.origin[1] - (-100 + offset[1]))

    if te0_coupling_len <= 120:
        te2_org = (ring_org[0], ring_org[1] - (te2_width/2 + racetrack_width/2 + te2_gap))
        te2_wg_r = Waveguide.make_at_port(Port(origin=te2_org, angle=0, width=te2_width))
        te2_wg_r.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_r.add_bend(radius=25, angle=-np.pi/4)
        te2_wg_r.add_bend(radius=25, angle=np.pi/4)
        te2_wg_r.add_straight_segment(length=offset[0] + 125 - 25 - te2_wg_r.origin[0])
        te2_wg_r.add_bend(radius=25, angle=-np.pi/2)
        te2_wg_r.add_straight_segment(length=te2_wg_r.origin[1] - (-100 + offset[1]))


        te2_wg_l = Waveguide.make_at_port(Port(origin=te2_org, angle=np.pi, width=te2_width))
        te2_wg_l.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_l.add_bend(radius=25, angle=np.pi/4)
        te2_wg_l.add_bend(radius=25, angle=-np.pi/4)
        te2_wg_l.add_straight_segment(length=te2_wg_l.origin[0] - (offset[0] - 125 + 25) )
        te2_wg_l.add_bend(radius=25, angle=np.pi/2)
        te2_wg_l.add_straight_segment(length=te2_wg_l.origin[1] - (-100 + offset[1]))
    else:
        bending_radius = 125 - te2_coupling_len / 2
        te2_org = (ring_org[0], ring_org[1] - (te2_width/2 + racetrack_width/2 + te2_gap))
        te2_wg_r = Waveguide.make_at_port(Port(origin=te2_org, angle=0, width=te2_width))
        te2_wg_r.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_r.add_bend(radius=bending_radius, angle=-np.pi/2)
        te2_wg_r.add_straight_segment(length=te2_wg_r.origin[1] - (-100 + offset[1]))


        te2_wg_l = Waveguide.make_at_port(Port(origin=te2_org, angle=np.pi, width=te2_width))
        te2_wg_l.add_straight_segment(length=te2_coupling_len/2)
        te2_wg_l.add_bend(radius=bending_radius, angle=np.pi/2)
        te2_wg_l.add_straight_segment(length=te2_wg_l.origin[1] - (-100 + offset[1]))

    coupler1_params = {
        'width': 1.2,
        'full_opening_angle': np.deg2rad(40),  # 40
        'grating_period': 0.7,
        'grating_ff': 0.84,  # minigap = 30nm
        # 'ap_max_ff':0.85,
        'ap_max_ff':0.84,
        'n_gratings': 40,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 0,  # 20
}


    gc1 = GratingCoupler.make_traditional_coupler(origin=te0_wg_r.origin, **coupler1_params)
    gc2 = GratingCoupler.make_traditional_coupler(origin=te0_wg_l.origin, **coupler1_params)
    gc3 = GratingCoupler.make_traditional_coupler(origin=te2_wg_r.origin, **coupler1_params)
    gc4 = GratingCoupler.make_traditional_coupler(origin=te2_wg_l.origin, **coupler1_params)

    # cell.add_to_layer(1, convert_to_positive_resist( [ring, te0_wg_r, te0_wg_l, te2_wg_r, te2_wg_l,
    #                                                 gc1, gc2, gc3, gc4],  buffer_radius=5))

    cell.add_to_layer(1, convert_to_positive_resist( [ring, te2_wg_r, te2_wg_l,
                                                    gc3, gc4],  buffer_radius=5))
    return cell

def make_racetrack_ring_omr(cell, upper_width=1.2, lower_width=1.2, racetrack_width=1.2, upper_gap=0.1, lower_gap=0.1, upper_coupling_len=100, lower_coupling_len=17,
                        racetrack_len = 200, right_gap=0.085, right_width=0.39, right_coupling_len=20,
                        offset=(0,0)):
    '''
    upper is upper wg,
    lower is buttom wg.
    '''
    ring_org = offset
    ring = Waveguide.make_at_port(Port(origin=ring_org, angle=0, width=racetrack_width))
    ring.add_straight_segment(length = racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi/2)
    right_origin = ring.origin
    ring.add_bend(radius=50, angle=np.pi/2)
    ring.add_straight_segment(length = racetrack_len / 2)
    pos = ring.origin
    aco_org = (pos[0], pos[1] + 0.5 + racetrack_width)
    ring.add_straight_segment(length = racetrack_len / 2)
    ring.add_bend(radius=50, angle=np.pi/2)
    ring.add_bend(radius=50, angle=np.pi/2)
    ring.add_straight_segment(length = racetrack_len / 2)   

    aco_wg_r = Waveguide.make_at_port(Port(origin=aco_org, angle=0, width=racetrack_width))
    aco_wg_r.add_straight_segment(length=20)
    aco_wg_r.add_bend(radius=50, angle=np.pi/2)
    aco_wg_r.add_straight_segment(length=20, final_width=0.001)

    aco_wg_l = Waveguide.make_at_port(Port(origin=aco_org, angle=-np.pi, width=racetrack_width))
    aco_wg_l.add_straight_segment(length=20)
    aco_wg_l.add_bend(radius=50, angle=-np.pi/2)
    aco_wg_l.add_straight_segment(length=20, final_width=0.001)



    upper_org = (pos[0], pos[1] + (upper_width/2 + racetrack_width/2 + upper_gap))
    upper_wg_r = Waveguide.make_at_port(Port(origin=upper_org, angle=0, width=upper_width))
    upper_wg_r.add_straight_segment(length=upper_coupling_len/2)
    upper_wg_r.add_bend(radius=40, angle=np.pi/4)
    upper_wg_r.add_bend(radius=40, angle=-np.pi/4)
    upper_wg_r.add_straight_segment(length=offset[0] + 375 - upper_wg_r.origin[0] - 50)
    upper_wg_r.add_bend(radius=50, angle=-np.pi/2)
    upper_wg_r.add_straight_segment(length=upper_wg_r.origin[1] - (-100 + offset[1]))
    upper_wg_l = Waveguide.make_at_port(Port(origin=upper_org, angle=np.pi, width=upper_width))
    upper_wg_l.add_straight_segment(length=upper_coupling_len/2)
    upper_wg_l.add_bend(radius=40, angle=-np.pi/4)
    upper_wg_l.add_bend(radius=40, angle=np.pi/4)
    upper_wg_l.add_straight_segment(length= upper_wg_l.origin[0] -(offset[0] - 375 + 50))
    upper_wg_l.add_bend(radius=50, angle=np.pi/2)
    upper_wg_l.add_straight_segment(length=upper_wg_l.origin[1] - (-100 + offset[1]))

    if lower_coupling_len <= 120:
        lower_org = (ring_org[0], ring_org[1] - (lower_width/2 + racetrack_width/2 + lower_gap))
        lower_wg_r = Waveguide.make_at_port(Port(origin=lower_org, angle=0, width=lower_width))
        lower_wg_r.add_straight_segment(length=lower_coupling_len/2)
        lower_wg_r.add_bend(radius=25, angle=-np.pi/4)
        lower_wg_r.add_bend(radius=25, angle=np.pi/4)
        lower_wg_r.add_straight_segment(length=offset[0] + 125 - 25 - lower_wg_r.origin[0])
        lower_wg_r.add_bend(radius=25, angle=-np.pi/2)
        lower_wg_r.add_straight_segment(length=lower_wg_r.origin[1] - (-100 + offset[1]))


        lower_wg_l = Waveguide.make_at_port(Port(origin=lower_org, angle=np.pi, width=lower_width))
        lower_wg_l.add_straight_segment(length=lower_coupling_len/2)
        lower_wg_l.add_bend(radius=25, angle=np.pi/4)
        lower_wg_l.add_bend(radius=25, angle=-np.pi/4)
        lower_wg_l.add_straight_segment(length=lower_wg_l.origin[0] - (offset[0] - 125 + 25) )
        lower_wg_l.add_bend(radius=25, angle=np.pi/2)
        lower_wg_l.add_straight_segment(length=lower_wg_l.origin[1] - (-100 + offset[1]))
    else:
        bending_radius = 125 - lower_coupling_len / 2
        lower_org = (ring_org[0], ring_org[1] - (lower_width/2 + racetrack_width/2 + lower_gap))
        lower_wg_r = Waveguide.make_at_port(Port(origin=lower_org, angle=0, width=lower_width))
        lower_wg_r.add_straight_segment(length=lower_coupling_len/2)
        lower_wg_r.add_bend(radius=bending_radius, angle=-np.pi/2)
        lower_wg_r.add_straight_segment(length=lower_wg_r.origin[1] - (-100 + offset[1]))


        lower_wg_l = Waveguide.make_at_port(Port(origin=lower_org, angle=np.pi, width=lower_width))
        lower_wg_l.add_straight_segment(length=lower_coupling_len/2)
        lower_wg_l.add_bend(radius=bending_radius, angle=np.pi/2)
        lower_wg_l.add_straight_segment(length=lower_wg_l.origin[1] - (-100 + offset[1]))

    right_bending_radius = 50+right_gap/2+right_width/2+racetrack_width/2
    right_bending_angle = right_coupling_len/2 / right_bending_radius

    right_wg_org = (right_origin[0] + right_gap + right_width/2 + racetrack_width/2, right_origin[1])
    right_wg_u = Waveguide.make_at_port(Port(origin=right_wg_org, angle=np.pi/2, width=right_width))
    right_wg_u.add_bend(radius=right_bending_radius, angle=right_bending_angle)
    right_wg_u.add_bend(radius=30, angle=-(np.pi/2 + right_bending_angle))
    right_wg_u.add_straight_segment(625 - 50 - (right_wg_u.origin[0] - offset[0]))
    right_wg_u.add_bend(radius=50, angle=-np.pi/2)
    right_wg_u.add_straight_segment(right_wg_u.origin[1] - lower_wg_l.origin[1])

    right_wg_l = Waveguide.make_at_port(Port(origin=right_wg_org, angle=-np.pi/2, width=right_width))
    right_wg_l.add_bend(radius=right_bending_radius, angle=-right_bending_angle)
    right_wg_l.add_bend(radius=30, angle=(np.pi/2 + right_bending_angle))
    right_wg_l.add_straight_segment(375 - 50 - (right_wg_l.origin[0] - offset[0]))
    right_wg_l.add_bend(radius=50, angle=-np.pi/2)
    right_wg_l.add_straight_segment(right_wg_l.origin[1] - lower_wg_l.origin[1])

    coupler1_params = {
        'width': lower_width,
        'full_opening_angle': np.deg2rad(40),  # 40
        'grating_period': 0.7,
        'grating_ff': 0.84,  # minigap = 30nm
        # 'ap_max_ff':0.85,
        'ap_max_ff':0.84,
        'n_gratings': 40,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 0,  # 20
    }

    coupler2_params = {
        'width': right_width,
        'full_opening_angle': np.deg2rad(40),  # 40
        'grating_period': 0.7,
        'grating_ff': 0.84,  # minigap = 30nm
        # 'ap_max_ff':0.85,
        'ap_max_ff':0.84,
        'n_gratings': 40,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 0,  # 20
    }

    gc1 = GratingCoupler.make_traditional_coupler(origin=lower_wg_r.origin, **coupler1_params)
    gc2 = GratingCoupler.make_traditional_coupler(origin=lower_wg_l.origin, **coupler1_params)
    gc3 = GratingCoupler.make_traditional_coupler(origin=right_wg_u.origin, **coupler2_params)
    gc4 = GratingCoupler.make_traditional_coupler(origin=right_wg_l.origin, **coupler2_params)

    # cell.add_to_layer(1, convert_to_positive_resist( [ring, upper_wg_r, upper_wg_l, lower_wg_r, lower_wg_l,
    #                                                 gc1, gc2, gc3, gc4],  buffer_radius=5))

    cell.add_to_layer(1, convert_to_positive_resist( [ring, lower_wg_r, lower_wg_l, gc1, gc2,
                                                    gc3, gc4, right_wg_u, right_wg_l, aco_wg_l, aco_wg_r],  buffer_radius=5))
    return cell

def make_poly_ring(cell, ring_radius=50, ring_width=1.2, wg_width=0.9, gap=0.07, coupling_len=20,
                        offset=(0,0)):

    ring_org = offset
    ring = Waveguide.make_at_port(Port(origin=ring_org, angle=0, width=ring_width))
    ring.add_bend(radius=ring_radius, angle=np.pi/2)
    ring.add_bend(radius=ring_radius, angle=np.pi/2)
    ring.add_bend(radius=ring_radius, angle=np.pi/2)
    ring.add_bend(radius=ring_radius, angle=np.pi/2)
    # pos = ring_org
    wg_r = Waveguide.make_at_port(Port(origin=(ring_org[0], ring_org[1] - ring_width/2 - wg_width/2 - gap), angle=0, width=wg_width))
    wg_radius = ring_radius + ring_width/2 + gap + wg_width/2
    coupling_angle = coupling_len / wg_radius / 2
    wg_r.add_bend(radius=wg_radius, angle=coupling_angle)
    wg_r.add_bend(radius=40, angle=-coupling_angle)
    pos = wg_r.origin

    if coupling_len < 90:
        wg_r.add_straight_segment(length=offset[0] + 75 - pos[0])
        wg_r.add_bend(radius=50, angle=-np.pi/2)
    else:
        wg_r.add_bend(radius=offset[0] + 125 - pos[0], angle=-np.pi/2)

    pos = wg_r.origin
    wg_r.add_straight_segment(length=pos[1] - (offset[1] - 100))

    wg_l = Waveguide.make_at_port(Port(origin=(ring_org[0], ring_org[1] - ring_width/2 - wg_width/2 - gap), angle=-np.pi, width=wg_width))
    wg_l.add_bend(radius=wg_radius, angle=-coupling_angle)
    wg_l.add_bend(radius=40, angle=coupling_angle)
    pos = wg_l.origin

    if coupling_len < 90:
        wg_l.add_straight_segment(length=abs(offset[0] - 75 - pos[0]))
        wg_l.add_bend(radius=50, angle=np.pi/2)
    else:
        wg_l.add_bend(radius=abs(offset[0] - 125 - pos[0]), angle=np.pi/2)
    
    pos = wg_l.origin
    wg_l.add_straight_segment(length=pos[1] - (offset[1] - 100))


    coupler1_params = {
        'width': wg_width,
        'full_opening_angle': np.deg2rad(40),  # 40
        'grating_period': 0.7,
        'grating_ff': 0.84,  # minigap = 30nm
        # 'ap_max_ff':0.85,
        'ap_max_ff':0.99,
        'n_gratings': 20,  # 20
        'taper_length': 16,  # 16um
        'n_ap_gratings': 20,  # 20
    }

    gc1 = GratingCoupler.make_traditional_coupler(origin=wg_r.origin, **coupler1_params)
    gc2 = GratingCoupler.make_traditional_coupler(origin=wg_l.origin, **coupler1_params)
    # gc3 = GratingCoupler.make_traditional_coupler(origin=te2_wg_r.origin, **coupler1_params)
    # gc4 = GratingCoupler.make_traditional_coupler(origin=te2_wg_l.origin, **coupler1_params)

    cell.add_to_layer(1, convert_to_positive_resist( [ring, wg_r, wg_l, gc1, gc2] ,buffer_radius=5))

    return cell