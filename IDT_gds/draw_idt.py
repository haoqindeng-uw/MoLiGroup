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
from gdshelpers.geometry import geometric_union
from gdshelpers.helpers.under_etching import create_holes_for_under_etching
from gdshelpers.geometry.ebl_frame_generators import raith_marker_frame
from gdshelpers.parts.text import Text
import CM_basic_code
import gdshelpers.geometry
    
def rectangular_xywh(center_x, center_y, length, width):
    outer_corners = [(center_x - length / 2, center_y - width / 2),
                     (center_x - length / 2, center_y + width / 2),
                     (center_x + length / 2, center_y + width / 2),
                     (center_x + length / 2, center_y - width / 2)]
    polygon = Polygon(outer_corners)
    return polygon

def make_idt(cell=None, pos=[0,0], pair=False, aperture=15, pair_num=50, pitch=1.6, finger_bias=0.005,
            zno=False, orientation='right', pair_distance=0, displacement_y=0):

    '''fingers'''
    finger_offset = 0.75
    top_fingers = None
    bottom_fingers = None

    finger_width = pitch/4 - finger_bias
    finger_len = aperture
    finger_center_x = pos[0]- finger_width/2
    finger_center_y = pos[1] 

    top_fingers = None
    bottom_fingers = None

    for i in range(pair_num * 2):
        finger = rectangular_xywh(center_x=finger_center_x, center_y=finger_center_y, length=finger_width, width=aperture)
        if i%2 == 0:
            if top_fingers is None:
                top_fingers = finger
            else:
                top_fingers = geometric_union([top_fingers, finger])
        else:
            if bottom_fingers is None:
                bottom_fingers = finger
            else:
                bottom_fingers = geometric_union([bottom_fingers, finger])
        finger_center_x = finger_center_x - pitch/2

    top_fingers = translate(top_fingers, yoff=finger_offset)
    bottom_fingers = translate(bottom_fingers, yoff=-finger_offset)

    '''arms'''
    top_arm_origin = [pos[0], pos[1] + aperture/2]
    bottom_arm_origin = [pos[0], pos[1] - aperture/2]
    arm_len = pitch * pair_num + 10
    arm_width = 5
    top_arm_center_x = pos[0] - arm_len/2 + 5
    top_arm_center_y = pos[1] + aperture/2 + arm_width/2
    top_arm = rectangular_xywh(center_x=top_arm_center_x, center_y=top_arm_center_y, length=arm_len, width=arm_width)

    bottom_arm_center_x = pos[0] - arm_len/2 + 5
    bottom_arm_center_y = pos[1] - aperture/2 - arm_width/2
    bottom_arm = rectangular_xywh(center_x=bottom_arm_center_x, center_y=bottom_arm_center_y, length=arm_len, width=arm_width)

    idt = geometric_union([top_arm, bottom_arm, top_fingers, bottom_fingers])

    '''pads'''
    pad_gap = 12
    len_tot = 450

    pad3_len = 250
    pad3_center_x = pos[0] - arm_len - pad3_len/2 - 30
    pad3_center_y = pos[1] + aperture/2 - 30 - pad_gap/2

    pad3_width = 60 - pad_gap
    pad3 = rectangular_xywh(center_x=pad3_center_x, center_y=pad3_center_y, length=pad3_len, width=60 - pad_gap)

    pad4_width = 60 + pad_gap
    pad4_len = 40
    pad4_center_x = pad3_center_x - pad3_len/2 - pad_gap - pad4_len/2
    pad4_center_y = pos[1] + aperture/2 - 30 - pad_gap/2
    pad4 = rectangular_xywh(center_x=pad4_center_x, center_y=pad4_center_y, length=pad4_len, width=60 + pad_gap)

    pad2_center_x = ((pad3_center_x + pad3_len/2) + (pos[0] + 2)) / 2
    pad2_center_y = pos[1] - aperture/2 - 60
    pad2_len = (pos[0] + 2) - (pad3_center_x + pad3_len/2)
    pad2_width = 120
    pad2 = rectangular_xywh(center_x=pad2_center_x, center_y=pad2_center_y, length=pad2_len, width=120)

    pad1_center_x = (pos[0] + 2 + (pad4_center_x - pad4_len/2)) / 2
    pad1_len = pos[0] + 2 - (pad4_center_x - pad4_len/2)
    pad1_center_y= pos[1] + aperture/2 + 60
    pad1 = rectangular_xywh(center_x=pad1_center_x, center_y=pad1_center_y, length=pad1_len, width=120)
    
    pad5_center_x = (pad1_center_x - pad1_len/2  + (pad2_center_x - pad2_len/2 - pad_gap)) / 2
    pad5_len = ((pad2_center_x - pad2_len/2 - pad_gap) - (pad1_center_x - pad1_len/2))
    pad5_center_y = (pad3_center_y - pad3_width/2 - pad_gap + (pos[1] - aperture/2 - 120)) / 2
    pad5_width = pad3_center_y - pad3_width/2 - pad_gap - (pad2_center_y - pad2_width/2)
    pad5 = rectangular_xywh(center_x=pad5_center_x, center_y=pad5_center_y, length=pad5_len, width=pad5_width)

    pads = geometric_union([pad1, pad2, pad3, pad4, pad5])
    pads = translate(pads, xoff=-(arm_len-3))
    pads = pads.buffer(3, join_style=1).buffer(-2, join_style=1)

    '''zno pads'''
    zno_pad = rectangular_xywh(center_x=pad1_center_x, center_y=pos[1], length=pad1_len, width=240+aperture)
    zno_pad = zno_pad.buffer(6)



    '''idt pair'''
    if pair is True:
        mirror_center_x = pos[0] + pair_distance/2
        pads_mirror = scale(pads, xfact=-1.0, origin=(mirror_center_x, 0))
        idt_mirror = scale(idt, xfact=-1.0, origin=(mirror_center_x, 0))
        zno_pad_mirror = scale(zno_pad, xfact=-1.0, origin=(mirror_center_x, 0))
        
        pads_mirror = translate(pads_mirror, yoff=displacement_y)
        idt_mirror = translate(idt_mirror, yoff=displacement_y) 
        zno_pad_mirror = translate(zno_pad_mirror, yoff=displacement_y)

        if cell is not None:
            if zno is True:
                cell.add_to_layer(2, geometric_union([zno_pad, zno_pad_mirror]))
            cell.add_to_layer(3, geometric_union([idt, idt_mirror]))
            cell.add_to_layer(4, geometric_union([pads, pads_mirror]))

        pos_mirror = [pos[0] + pair_distance, pos[1] + displacement_y]

        return cell, idt, idt_mirror, pads, pads_mirror, zno_pad, zno_pad_mirror, pos, pos_mirror

    else:
        if orientation == 'left':
            mirror_center_x = pos[0]
            pads = scale(pads, xfact=-1.0, origin=(mirror_center_x, 0))
            idt = scale(idt, xfact=-1.0, origin=(mirror_center_x, 0))
            zno_pad = scale(zno_pad, xfact=-1.0, origin=(mirror_center_x, 0))

        if cell is not None:
            if zno is True:
                cell.add_to_layer(2, zno_pad)
            cell.add_to_layer(3, idt)
            cell.add_to_layer(4, pads)

    return cell, idt, pads, zno_pad, pos