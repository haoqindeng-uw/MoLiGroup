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

def make_IDT_stright_delayline(cell: Cell, prop_len=200, wg_width=1.2, finger_width=0.445, number_of_pairs=80, IDT_Aperature=15, 
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

