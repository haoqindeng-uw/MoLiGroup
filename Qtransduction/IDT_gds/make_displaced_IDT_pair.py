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

def make_displaced_IDT_pairs(figer_widths, number_of_pairs, IDT_Aperature, prop_length, y_displacement):
    # Creat the IDT
    # Change parameter here:

    # How many pairs of IDT fingers
    number_of_pairs = int(number_of_pairs)
    how_many_period = number_of_pairs

    # Finger coordinate (correction of different IDT aperature)
    Finger_origin_x = 0  # last two term = figers offset (5um) + small_pad_width_with extended(10um)
    Finger_origin_y = 0

    # Finger offset on the other side of the horn structure
    Finger_length = IDT_Aperature
    Finger_left_offset = prop_length
    # Pad coordinate
    arm2_right_pad_Offset = Finger_length + 4.5
    pad_length = how_many_period * 2

    # Below DO NOT CHANGE ------------------------------------------------------------------------------
    # one_period_arm2 = [finger_width, finger_width + pitch]
    IDT_sides = [1,2]
    side_2_reduction_factor = 1
    Idt_finger_arm1 = []
    Idt_finger_arm2 = []
    Idt_finger_arm3 = []
    Idt_finger_arm4 = []
    number_of_widths = 5
    #From data of BGaP on sapphire, the effective acoustic velocity is 4080m/s ~ for 680nm wavelength at 6GHz resonance
    """Update 06 02, for hight frequency single frequency IDT fingers, the starting width is 0.17 and end width is also 0.17 with 100 pairs, (total area is 170um sqare)
    for optomechanical ring resonator which is used for intermode scattering functions we want 670MHz IDT fingers, the pitch is ~4.48um, so the width is 4.48/4 = 1.12um"""

    start_width = figer_widths
    end_width = figer_widths
    litho_corrected_width = 0.005 #0.2 for 1um
    chirp_widths = np.linspace(start_width,end_width,number_of_widths)
    chirp_widths = chirp_widths[::-1]

    # Make the IDT that lunches the signal
    for side in IDT_sides:

        for index, width in enumerate(chirp_widths):
            pitch = 3 * width


            one_period_arm1 = [width - litho_corrected_width, pitch + litho_corrected_width]
            one_period_arm2 = one_period_arm1

            # Make sure the number of pairs can be equally devided into number of widths
            if (number_of_pairs / number_of_widths).is_integer() == True and side ==1:
                devided_pairs = int(number_of_pairs / number_of_widths)
                for i in range(devided_pairs):
                    # Control the IDT fingers number on side 1
                    # Change the period of the last pair in this pair group to the next pair's period
                    if i == devided_pairs - 1 and index != len(chirp_widths) - 1:
                        pitch1 = chirp_widths[index + 1] * 3  # pitch for the last ending finger
                        pitch2 = width * 2 + chirp_widths[index + 1] * 1  # pitch for the second last finger

                        one_period_arm1 = [width - litho_corrected_width, pitch1 + litho_corrected_width]
                        one_period_arm2 = [width - litho_corrected_width, pitch2 + litho_corrected_width]

                        Idt_finger_arm1.extend(one_period_arm1)
                        Idt_finger_arm2.extend(one_period_arm2)

                    else:
                        Idt_finger_arm1.extend(one_period_arm1)
                        Idt_finger_arm2.extend(one_period_arm2)
            #Control the IDT fingers number on side 2
            elif (number_of_pairs / number_of_widths).is_integer() == True and side ==2:
                devided_pairs = int(number_of_pairs / number_of_widths / side_2_reduction_factor)
                for i in range(devided_pairs):

                    # Change the period of the last pair in this pair group to the next pair's period
                    if i == devided_pairs - 1 and index != len(chirp_widths) - 1:
                        pitch1 = chirp_widths[index + 1] * 3  # pitch for the last ending finger
                        pitch2 = width * 2 + chirp_widths[index + 1] * 1  # pitch for the second last finger

                        one_period_arm1 = [width - litho_corrected_width, pitch1 + litho_corrected_width]
                        one_period_arm2 = [width - litho_corrected_width, pitch2 + litho_corrected_width]

                        Idt_finger_arm3.extend(one_period_arm1)
                        Idt_finger_arm4.extend(one_period_arm2)

                    else:
                        Idt_finger_arm3.extend(one_period_arm1)
                        Idt_finger_arm4.extend(one_period_arm2)
            else:
                print("%0.1f pairs can not be evenly devided into %0.1f different widths" % (
                number_of_pairs, number_of_widths))
                break

    # Below DO NOT CHANGE ------------------------------------------------------------------------------

    # IDT ON THE "right" GRATING COUPLER
    # Finger_lower1 is lower idt fingers, Finger_upper1 is upper IDT finger (on the horn on the right)
    # If you want to make chirp fingers, add 0.02 to the finger_upper1 line e.g.  Finger_origin_x + 2*(chirp_widths[-1]) +0.02
    # Funger_upper_other_side1 = Finger_origin_x - Finger_left_offset - 2*(chirp_widths[-1]) - 0.02
    up_down_finger_offset = 1
    up_down_finger_offset = 0.75
    finger_y_offset = -2.25

    Finger_lower1 = Waveguide.make_at_port(
        Port(origin=(Finger_origin_x , Finger_origin_y - up_down_finger_offset + IDT_Aperature + finger_y_offset), angle=-np.pi/2, width=Idt_finger_arm1))
    Finger_lower1.add_straight_segment(length=Finger_length + 0.25)


    Finger_upper1 = Waveguide.make_at_port(
        Port(origin=(Finger_origin_x + 2*(chirp_widths[-1]) , Finger_origin_y + IDT_Aperature +finger_y_offset), angle=-np.pi/2,
             width=Idt_finger_arm2))
    Finger_upper1.add_straight_segment(length=Finger_length + 0.25)


    # SAME IDT ON THE "left" side ---------------------------------------------------------------------------------------------------
    # Finger_lower_other_side is left IDT finger, wg_2 is right IDT finger
    Finger_lower_other_side1 = Waveguide.make_at_port(Port(origin=(Finger_origin_x - Finger_left_offset , Finger_origin_y- up_down_finger_offset +finger_y_offset), angle=np.pi/2, width=Idt_finger_arm3))
    Finger_lower_other_side1.add_straight_segment(length = Finger_length + 0.25)


    Finger_upper_other_side1 = Waveguide.make_at_port(Port(origin=(Finger_origin_x - Finger_left_offset - 2*(chirp_widths[-1]), Finger_origin_y +finger_y_offset), angle=np.pi / 2, width=Idt_finger_arm4))
    Finger_upper_other_side1.add_straight_segment(length=Finger_length + 0.25) #+ - 0.4 for 1um finger


    # Make Small metal pad
    finger_y_position_bot = Finger_origin_y + 2
    finger_y_position_top = Finger_origin_y - 2
    average_chirp_finger_width = (start_width + end_width) / 2
    average_chirp_finger_pitch = average_chirp_finger_width * 4
    Chirped_finger_gap_offsets = (average_chirp_finger_width + average_chirp_finger_pitch) / 2 + average_chirp_finger_width / 2

    shift_2 = number_of_pairs*(average_chirp_finger_pitch)/1.8
    print('shift 2: ', shift_2)
    right_small_pad_right_offset = shift_2 / 10
    # right_small_pad_right_offset = shift_2 / 50
    left_small_pad_left_offset = right_small_pad_right_offset
    #Left_bot
    outer_corners_arm2_1 = [
        (Finger_origin_x + shift_2 - Finger_left_offset - left_small_pad_left_offset, finger_y_position_bot - 10),
        (Finger_origin_x + shift_2 - Finger_left_offset - left_small_pad_left_offset, finger_y_position_bot - 5),
        (Finger_origin_x - shift_2 - Finger_left_offset - left_small_pad_left_offset, finger_y_position_bot - 5),
        (Finger_origin_x - shift_2 - Finger_left_offset - left_small_pad_left_offset, finger_y_position_bot - 10)]
    # Left_top
    outer_corners_arm2_2 = [(Finger_origin_x + shift_2 - Finger_left_offset - left_small_pad_left_offset ,finger_y_position_top + arm2_right_pad_Offset),
                            (Finger_origin_x + shift_2 - Finger_left_offset - left_small_pad_left_offset ,finger_y_position_top + arm2_right_pad_Offset - 5),
                            (Finger_origin_x - shift_2 - Finger_left_offset - left_small_pad_left_offset ,finger_y_position_top + arm2_right_pad_Offset - 5),
                            (Finger_origin_x - shift_2 - Finger_left_offset - left_small_pad_left_offset ,finger_y_position_top + arm2_right_pad_Offset)]
    left_x_coord_TR = Finger_origin_x + shift_2 - Finger_left_offset - left_small_pad_left_offset
    left_y_coord_TR = finger_y_position_top + arm2_right_pad_Offset - 5 
    # --------------------------------------------------------------------------------------------------------------
    # Right_bot small pad------------------------------------------------------------------------------------------------

    print('debug shift: ', Finger_origin_x, shift_2, right_small_pad_right_offset)
    outer_corners_arm1_1 = [(Finger_origin_x - shift_2 + right_small_pad_right_offset, finger_y_position_bot - 10),
                            # Bot-left corner
                            (Finger_origin_x - shift_2 + right_small_pad_right_offset, finger_y_position_bot - 5),
                            # Bot-left corner
                            (Finger_origin_x + shift_2 + right_small_pad_right_offset + 10, finger_y_position_bot - 5) ,
                            # Top-Right corner
                            (Finger_origin_x + shift_2 + right_small_pad_right_offset + 10, finger_y_position_bot - 10)
                            # Top-left corner
                            ]

    # Right_top small pad-----------------------------------------------------------------------------------------------
    outer_corners_arm1_2 = [
        (Finger_origin_x - shift_2 + right_small_pad_right_offset, finger_y_position_top + arm2_right_pad_Offset - 0),
        # Bot-right corner
        (Finger_origin_x - shift_2 + right_small_pad_right_offset, finger_y_position_top + arm2_right_pad_Offset - 5),
        # Bot-left corner
        (Finger_origin_x + shift_2 + right_small_pad_right_offset + 10, finger_y_position_top + arm2_right_pad_Offset - 5),  # Top-left corner
        (Finger_origin_x + shift_2 + right_small_pad_right_offset + 10, finger_y_position_top + arm2_right_pad_Offset - 0)]  # Top-right corner
    print('specifically debug arm1-2: ', outer_corners_arm1_2)

    y_mid_IDT = Finger_origin_y + arm2_right_pad_Offset/2
    right_top_small_pad_TL_X = Finger_origin_x - shift_2 + right_small_pad_right_offset
    right_top_small_pad_TL_Y = Finger_origin_y + arm2_right_pad_Offset - 0

    # Make big metal pads
    # Left Big pad bot
    bot_left_y = Finger_origin_y - 5.5
    bot_left_x = Finger_origin_x - shift_2 - Finger_left_offset - left_small_pad_left_offset + 2

    X_tr = bot_left_x + 50
    Y_tr = bot_left_y  # TOP_RIGHT

    X_tl = X_tr - 300
    Y_tl = Y_tr  # TOP_LEFT

    X_bl_ext1 = X_tl
    Y_bl_ext1 = Y_tl - 60  # BOT_left extend to middle upper point

    X_bl_ext2 = X_bl_ext1 + 290
    Y_bl_ext2 = Y_bl_ext1  # BOT_RIGHT extend to middle lower point

    X_bl = X_bl_ext2
    Y_bl = Y_bl_ext2 - 150  # BOT_LEFT:

    # The big pad middle point in the middle of the IDT
    # Lower middle point
    X_br = X_tr + 70 # 70 before june 19 
    Y_br = Y_bl  # BOT_RIGHT 
    # Upper middle point
    X_br_ext1 = X_br
    Y_br_ext1 = Y_br + 100

    buffer_cord_x = X_tl
    buffer_cord_y = Y_tl
    buffer_cord_x2 = X_bl_ext2
    buffer_cord_y2 = Y_bl_ext1
    buffer_cord_x3 = X_br

    Outer_corners_Big_pad1_1 = [(X_tr, Y_tr),
                                (X_tl, Y_tl),
                                (X_bl_ext1, Y_bl_ext1),
                                (X_bl_ext2, Y_bl_ext2),
                                (X_bl, Y_bl),
                                (X_br, Y_br),
                                (X_br_ext1, Y_br_ext1)
                                ]
    # Left Big pad top
    top_right_y = Finger_origin_y + arm2_right_pad_Offset
    top_right_x = Finger_origin_x - shift_2 - Finger_left_offset - left_small_pad_left_offset + 4

    X_tr = top_right_x
    Y_tr = top_right_y  # TOP_RIGHT

    X_tl = buffer_cord_x - 50
    Y_tl = Y_tr  # TOP_LEFT

    X_bl_ext1 = X_tl
    Y_bl_ext1 = buffer_cord_y2 - 150  # BOT_left extend to middle upper point

    X_bl_ext2 = buffer_cord_x2 - 10
    Y_bl_ext2 = Y_bl_ext1  # BOT_RIGHT extend to middle lower point

    X_bl_ext3 = X_bl_ext2
    Y_bl_ext3 = buffer_cord_y2 - 10  # BOT_RIGHT extend to middle lower point

    X_bl_ext4 = buffer_cord_x - 10
    Y_bl_ext4 = Y_bl_ext3

    X_bl = X_bl_ext4
    Y_bl = buffer_cord_y + 10  # BOT_LEFT:

    X_br = X_tr
    Y_br = Y_bl  # BOT_RIGHT

    Outer_corners_Big_pad1_2 = [(X_tr, Y_tr),
                                (X_tl, Y_tl),
                                (X_bl_ext1, Y_bl_ext1),
                                (X_bl_ext2, Y_bl_ext2),
                                (X_bl_ext3, Y_bl_ext3),
                                (X_bl_ext4, Y_bl_ext4),
                                (X_bl, Y_bl),
                                (X_br, Y_br)
                                ]
    # -----Right big pad bot
    bot_right_x = Finger_origin_x + shift_2 + right_small_pad_right_offset - 2
    bot_right_y = Finger_origin_y - 5.5

    X_tr = bot_right_x - 50
    Y_tr = bot_right_y  # TOP_RIGHT

    X_tl = X_tr + 300
    Y_tl = Y_tr  # TOP_LEFT

    X_bl_ext1 = X_tl
    Y_bl_ext1 = Y_tl - 60  # BOT_left extend to middle upper point

    X_bl_ext2 = X_bl_ext1 - 290
    Y_bl_ext2 = Y_bl_ext1  # BOT_RIGHT extend to middle lower point

    X_bl = X_bl_ext2
    Y_bl = Y_bl_ext2 - 151  # BOT_LEFT:

    # The middle point of the right bigpad
    # Lower middle point
    X_br = X_bl_ext2 -70
    # Upper middle point
    Y_br = Y_bl  # BOT_RIGHT

    X_br_ext1 = X_br
    Y_br_ext1 = Y_br + 100

    buffer_cord_x = X_tl
    buffer_cord_y = Y_tl
    buffer_cord_x2 = X_bl_ext2
    buffer_cord_y2 = Y_bl_ext1

    Outer_corners_Big_pad2_1 = [(X_tr, Y_tr),
                                (X_tl, Y_tl),
                                (X_bl_ext1, Y_bl_ext1),
                                (X_bl_ext2, Y_bl_ext2),
                                (X_bl, Y_bl),
                                (X_br, Y_br),
                                (X_br_ext1, Y_br_ext1)
                                ]
    # Right top big pad
    top_right_y = Finger_origin_y + arm2_right_pad_Offset - 0
    top_right_x = bot_right_x - 2

    X_tr = top_right_x
    Y_tr = top_right_y  # TOP_RIGHT

    X_tl = buffer_cord_x + 50
    Y_tl = Y_tr  # TOP_LEFT

    X_bl_ext1 = X_tl
    Y_bl_ext1 = buffer_cord_y2 - 151  # BOT_left extend to middle upper point

    X_bl_ext2 = buffer_cord_x2 + 10
    Y_bl_ext2 = Y_bl_ext1  # BOT_RIGHT extend to middle lower point

    X_bl_ext3 = X_bl_ext2
    Y_bl_ext3 = buffer_cord_y2 - 10  # BOT_RIGHT extend to middle lower point

    X_bl_ext4 = buffer_cord_x + 10
    Y_bl_ext4 = Y_bl_ext3

    X_bl = X_bl_ext4
    Y_bl = buffer_cord_y + 10  # BOT_LEFT:

    X_br = X_tr
    Y_br = Y_bl  # BOT_RIGHT

    Y_tr = 120
    Y_tl = 120

    # X_tr -= 100
    # X_br -= 100

    Outer_corners_Big_pad2_2 = [(X_tr, Y_tr),
                                (X_tl, Y_tl),
                                (X_bl_ext1, Y_bl_ext1),
                                (X_bl_ext2, Y_bl_ext2),
                                (X_bl_ext3, Y_bl_ext3),
                                (X_bl_ext4, Y_bl_ext4),
                                (X_bl, Y_bl),
                                (X_br, Y_br)
                                ]
    print('pad coordinates: ',  X_tr, X_tl, Y_tr, Y_tl, X_bl, Y_bl, X_br, Y_br)
    # --------------------------------------------------------------------------------------------------------------


    small_pad_arm2_1 = Polygon(outer_corners_arm2_1)
    small_pad_arm2_2 = Polygon(outer_corners_arm2_2)
    small_pad_arm1_1 = Polygon(outer_corners_arm1_1)
    small_pad_arm1_2 = Polygon(outer_corners_arm1_2)

    port_coordinates = [outer_corners_arm2_1, outer_corners_arm2_2, outer_corners_arm1_1, outer_corners_arm1_2]

    print(outer_corners_arm2_1)
    print(outer_corners_arm2_2)
    print(outer_corners_arm1_1)
    print(outer_corners_arm1_2)

    Big_pad1_1 = Polygon(Outer_corners_Big_pad1_1)
    Big_pad1_2 = Polygon(Outer_corners_Big_pad1_2)
    Big_pad2_1 = Polygon(Outer_corners_Big_pad2_1)
    Big_pad2_2 = Polygon(Outer_corners_Big_pad2_2)

    print('outer corner coordinates: ', Outer_corners_Big_pad2_2)

    fingers_and_smallpads = geometric_union([Finger_lower1, Finger_upper1, \
           Finger_lower_other_side1, Finger_upper_other_side1, \
           small_pad_arm1_1, small_pad_arm1_2 ,small_pad_arm2_1, small_pad_arm2_2])
    Big_pads = geometric_union([Big_pad1_1, Big_pad1_2, Big_pad2_1, Big_pad2_2])

    IDT_1 = geometric_union([Finger_lower1, Finger_upper1, small_pad_arm1_1, small_pad_arm1_2])
    IDT_2 = geometric_union([Finger_lower_other_side1, Finger_upper_other_side1, small_pad_arm2_1, small_pad_arm2_2])
    
    # IDT_1_bigpad = geometric_union([Big_pad2_1, Big_pad2_2])
    # IDT_2_bigpad = geometric_union([Big_pad1_1, Big_pad1_2])

    IDT_1_bigpad = geometric_union([Big_pad2_1, Big_pad2_2])
    IDT_2_bigpad = geometric_union([Big_pad1_1, Big_pad1_2])

    # IDT_1_bigpad = translate(IDT_1_bigpad, xoff=90, yoff=0)
    # IDT_2_bigpad = translate(IDT_2_bigpad, xoff=90, yoff=0)

    # Displace the IDT
    # IDT_2 = translate(IDT_2, yoff = y_displacement)
    # IDT_2_bigpad = translate(IDT_2_bigpad, yoff = y_displacement)
    
    return IDT_1, IDT_1_bigpad, \
           IDT_2, IDT_2_bigpad, \
           top_right_x, y_mid_IDT, shift_2, \
           right_top_small_pad_TL_X, right_top_small_pad_TL_Y, left_x_coord_TR, left_y_coord_TR, port_coordinates