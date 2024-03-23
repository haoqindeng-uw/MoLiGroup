
from shapely.geometry import Polygon

def make_ZnO_pads(zno_pad_x_length, right_top_small_pad_TL_X, right_top_small_pad_TL_Y, pad_width, left_x_coord_TR ):
    # Create ZnO

    # ZnO Expand
    ZnO_expand_x = 30
    ZnO_expand_y = 5
    ZnO_pad_width = pad_width
    Left_ZnO_OFFSET_X = 203
    y_offset = -3
    x_offset = 30
    # Make_ZnO_Pad
    Outer_corner_ZnO_pad_R = [(right_top_small_pad_TL_X - ZnO_expand_x + x_offset,  y_offset+ right_top_small_pad_TL_Y + ZnO_expand_y ), #Bot Right
                              (right_top_small_pad_TL_X + zno_pad_x_length + ZnO_expand_x + x_offset, y_offset+ right_top_small_pad_TL_Y + ZnO_expand_y), #Top Right
                              (right_top_small_pad_TL_X + zno_pad_x_length + ZnO_expand_x + x_offset, y_offset+ right_top_small_pad_TL_Y -ZnO_pad_width - ZnO_expand_y), #Top Left
                              (right_top_small_pad_TL_X - ZnO_expand_x + x_offset, y_offset+ right_top_small_pad_TL_Y -ZnO_pad_width - ZnO_expand_y)] #Bot Left

    Outer_corner_ZnO_pad_L = [(left_x_coord_TR + ZnO_expand_x  -x_offset, y_offset+ right_top_small_pad_TL_Y + ZnO_expand_y),   # Bot Right
                              (left_x_coord_TR - zno_pad_x_length - ZnO_expand_x  -x_offset, y_offset+ right_top_small_pad_TL_Y + ZnO_expand_y),  # Top Right
                              (left_x_coord_TR - zno_pad_x_length - ZnO_expand_x  -x_offset, y_offset+ right_top_small_pad_TL_Y - ZnO_pad_width - ZnO_expand_y),  # Top Left
                              (left_x_coord_TR + ZnO_expand_x  -x_offset, y_offset+ right_top_small_pad_TL_Y - ZnO_pad_width - ZnO_expand_y)]  # Bot Left

    ZnO_pad_R = Polygon(Outer_corner_ZnO_pad_R)
    ZnO_pad_L = Polygon(Outer_corner_ZnO_pad_L)


    return ZnO_pad_R, ZnO_pad_L