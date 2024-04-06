from math import pi, cos, sin, asin, tan
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.port import Port
from shapely.geometry import Polygon, Point
from gdshelpers.parts.interferometer import MachZehnderInterferometer
from gdshelpers.geometry.chip import Cell
import numpy as np
from gdshelpers.parts.text import Text

def triangle(vertice_1, vertice_2, vertice_3):
    outer_corners = [vertice_1, vertice_2, vertice_3]
    polygon = Polygon(outer_corners)
    return polygon

def rectangular_xywh(center_x, center_y, length, width):
    outer_corners = [(center_x - length / 2, center_y - width / 2),
                     (center_x - length / 2, center_y + width / 2),
                     (center_x + length / 2, center_y + width / 2),
                     (center_x + length / 2, center_y - width / 2)]
    polygon = Polygon(outer_corners)
    return polygon

def rhombus_xywh(center_x, center_y, length, width, angle):
    outer_corners = [(center_x - length / 2 - width/tan(angle/180 * pi)/2, center_y - width / 2),
                     (center_x - length / 2 + width/tan(angle/180 * pi)/2, center_y + width / 2),
                     (center_x + length / 2 + width/tan(angle/180 * pi)/2, center_y + width / 2),
                     (center_x + length / 2 - width/tan(angle/180 * pi)/2, center_y - width / 2)]
    polygon = Polygon(outer_corners)
    return polygon


def rectangular_xywh_rot(center_x, center_y, length, width, rot_angle):
    outer_corners = [(center_x - length * cos(rot_angle / 180 * pi) / 2 - width * sin(rot_angle / 180 * pi) / 2,
                      center_y - length * sin(rot_angle / 180 * pi) / 2 + width * cos(rot_angle / 180 * pi) / 2),
                     (center_x - length * cos(rot_angle / 180 * pi) / 2 + width * sin(rot_angle / 180 * pi) / 2,
                      center_y - length * sin(rot_angle / 180 * pi) / 2 - width * cos(rot_angle / 180 * pi) / 2),
                     (center_x + length * cos(rot_angle / 180 * pi) / 2 + width * sin(rot_angle / 180 * pi) / 2,
                      center_y + length * sin(rot_angle / 180 * pi) / 2 - width * cos(rot_angle / 180 * pi) / 2),
                     (center_x + length * cos(rot_angle / 180 * pi) / 2 - width * sin(rot_angle / 180 * pi) / 2,
                      center_y + length * sin(rot_angle / 180 * pi) / 2 + width * cos(rot_angle / 180 * pi) / 2)]
    polygon = Polygon(outer_corners)
    return polygon

def write_label(start_x, start_y, size, text, layer, cell_name):
    write_text = Text([start_x, start_y], size, text)
    cell_name.add_to_layer(layer, write_text)
    return cell_name


def local_mark(center_x, center_y, local_mark_params, layer, cell_name):
    polygon1 = rectangular_xywh(center_x, center_y, local_mark_params['length'], local_mark_params['width'])
    polygon2 = rectangular_xywh(center_x, center_y, local_mark_params['width'], local_mark_params['length'])
    cell_name.add_to_layer(layer, polygon1, polygon2)
    return cell_name


def local_mark_set(center_x, center_y, pitch_x, pitch_y, local_mark_params, layer, cell_name):
    local_mark(center_x - pitch_x/2, center_y - pitch_y/2, local_mark_params, layer, cell_name)
    local_mark(center_x - pitch_x/2, center_y + pitch_y/2, local_mark_params, layer, cell_name)
    local_mark(center_x + pitch_x/2, center_y + pitch_y/2, local_mark_params, layer, cell_name)
    local_mark(center_x + pitch_x/2, center_y - pitch_y/2, local_mark_params, layer, cell_name)
    return cell_name


def global_mark(center_x, center_y, global_mark_params, layer, cell_name):

    center_polygon = rectangular_xywh(center_x, center_y, global_mark_params['rectangular_dim'],
                                      global_mark_params['rectangular_dim'])
    local_mark(center_x - global_mark_params['rec_mark_spacing'], center_y, global_mark_params, layer, cell_name)
    local_mark(center_x, center_y + global_mark_params['rec_mark_spacing'], global_mark_params, layer, cell_name)
    local_mark(center_x + global_mark_params['rec_mark_spacing'], center_y, global_mark_params, layer, cell_name)
    local_mark(center_x, center_y - global_mark_params['rec_mark_spacing'], global_mark_params, layer, cell_name)
    cell_name.add_to_layer(layer, center_polygon)
    return cell_name


def trench(center_x, center_y, length, width, layer, cell_name):
    outer_corners = [(center_x - length / 2, center_y - width / 2),
                     (center_x - length / 2, center_y + width / 2),
                     (center_x + length / 2, center_y + width / 2),
                     (center_x + length / 2, center_y - width / 2)]
    polygon = Polygon(outer_corners)
    cell_name.add_to_layer(layer, polygon)
    return cell_name

def circle(center_x, center_y, radius, layer, cell_name):
    point = Point(center_x, center_y)
    circle = point.buffer(radius)
    cell_name.add_to_layer(layer, circle)
    return cell_name

def circle_array(center_x, center_y, x_num, y_num, period_x, period_y, radius, layer, cell_name):
    if x_num % 2 == 1:
        start_x = center_x - int(x_num / 2) * period_x
    else:
        start_x = center_x - x_num / 2.0 * period_x
    if y_num % 2 == 1:
        start_y = center_y - int(y_num / 2) * period_y
    else:
        start_y = center_y - y_num / 2.0 * period_y
    
    for i in range(x_num):
        for j in range(y_num):
            circle(
                start_x + i * period_x, 
                start_y + j * period_y, 
                radius, 
                layer,
                cell_name
            )
    return cell_name

def pcm_grid(center_x, center_y, length, width, pcm_grid_params, layer, cell_name, local_mark=True):
    nx = int(length / pcm_grid_params['pitch_x'])
    ny = int(width / pcm_grid_params['pitch_y'])
    # print('nx: ', nx, ' ny, ', ny)
    for i in range(0, nx):
        for j in range(0, ny):
            pcm_cell = rectangular_xywh(center_x - (nx / 2 - 0.5 - i) * pcm_grid_params['pitch_x'],
                                        center_y - (ny / 2 - 0.5 - j) * pcm_grid_params['pitch_y'],
                                        pcm_grid_params['pitch_x'] - pcm_grid_params['gap_x'],
                                        pcm_grid_params['pitch_y'] - pcm_grid_params['gap_y'])
            cell_name.add_to_layer(layer, pcm_cell)
            # print('gap_x: ', pcm_grid_params['gap_x'], end=', ')
            # print('gap_y: ', pcm_grid_params['gap_y'])
            # print('pitch_x: ', pcm_grid_params['pitch_x'], end=', ')
            # print('pitch_y: ', pcm_grid_params['pitch_y'])
            # print('pcm_grid_x: ', pcm_grid_params['pitch_x'] - pcm_grid_params['gap_x'], end=', ')
            # print('pcm_grid_y: ', pcm_grid_params['pitch_y'] - pcm_grid_params['gap_y'])
            if local_mark is True:
                dist = 10
                center_x_c = center_x - (nx / 2 - 0.5 - i) * pcm_grid_params['pitch_x']
                center_y_c = center_y - (ny / 2 - 0.5 - j) * pcm_grid_params['pitch_y']
                width_x_c = pcm_grid_params['pitch_x'] - pcm_grid_params['gap_x']
                width_y_c = pcm_grid_params['pitch_y'] - pcm_grid_params['gap_y']

                center_x_ul = center_x_c - width_x_c / 2.0
                center_y_ul = center_y_c + width_y_c / 2.0 + dist
                center_x_dl = center_x_c - width_x_c / 2.0
                center_y_dl = center_y_c - width_y_c / 2.0 - dist
                center_x_ur = center_x_c + width_x_c / 2.0
                center_y_ur = center_y_c + width_y_c / 2.0 + dist
                center_x_dr = center_x_c + width_x_c / 2.0
                center_y_dr = center_y_c - width_y_c / 2.0 - dist

                circle_array(center_x_ul, center_y_ul, 5, 5, 0.5, 0.5,
                                radius=0.125, layer=8, cell_name=cell_name)
                circle_array(center_x_dl, center_y_dl, 5, 5, 0.5, 0.5,
                                radius=0.125, layer=8, cell_name=cell_name)
                circle_array(center_x_ur, center_y_ur, 5, 5, 0.5, 0.5,
                                radius=0.125, layer=8, cell_name=cell_name)
                circle_array(center_x_dr, center_y_dr, 5, 5, 0.5, 0.5,
                                radius=0.125, layer=8, cell_name=cell_name)


    return cell_name


def wg_taper(start_x, start_y, length, width_1, width_2, angle):
    outer_corners = [(start_x - width_1 * sin(angle) / 2,
                      start_y + width_1 * cos(angle) / 2),
                     (start_x + length * cos(angle) - width_2 * sin(angle) / 2,
                      start_y + length * sin(angle) + width_2 * cos(angle) / 2),
                     (start_x + length * cos(angle) + width_2 * sin(angle) / 2,
                      start_y + length * sin(angle) - width_2 * cos(angle) / 2),
                     (start_x + width_1 * sin(angle) / 2,
                      start_y - width_1 * cos(angle) / 2)]
    polygon = Polygon(outer_corners)
    return polygon

def mode_converter(start_x, start_y, mode_converter_params, mc_type, layer, cell_name):    # mc type 'l--left r--right'
    h = (mode_converter_params['bending_height'] - mode_converter_params['gap'] / 2 -
         mode_converter_params['bot_wg_width'] / 2) / 2
    radius = (h ** 2 + mode_converter_params['bending_length'] ** 2 / 4) / (2 * h)
    angle = asin(mode_converter_params['bending_length'] / (2 * radius))
    d = mode_converter_params['bending_length'] / 2 - h / sin(2 * angle) - h / tan(2 * angle)
    x = 2 * d * sin(angle) ** 2
    y = x / tan(angle)
    y2=(radius-2.2)*(1-cos(2*angle))
    x2=(radius-2.2)*sin(2*angle)

    if mc_type.find('l') != -1:
        wg_bot = Waveguide.make_at_port(Port((start_x, start_y),
                                             angle=0, width=mode_converter_params['bot_wg_width']))
        wg_bot.add_straight_segment(length=mode_converter_params['guide_length'])
        wg_bot.add_bend(angle, radius=radius)
        wg_bot.add_bend(-angle, radius=radius)
        wg_bot.add_straight_segment(length=mode_converter_params['cpl_length'])
        wg_bot.add_bend(-angle, radius=radius - 2.2)
        wg_bot.add_bend(-angle, radius=radius - 2.2)
        wg_bot.add_straight_segment(length=5, final_width=[0.1])

    if mc_type.find('d') != -1:
        wg_right = Waveguide.make_at_port(Port((start_x, start_y),
                                             angle=pi/2, width=mode_converter_params['bot_wg_width']))
        wg_right.add_straight_segment(length=mode_converter_params['guide_length'])
        wg_right.add_bend(angle, radius=radius)
        wg_right.add_bend(-angle, radius=radius)
        wg_right.add_straight_segment(length=mode_converter_params['cpl_length'])
        wg_right.add_bend(-angle, radius=radius - 2.2)
        wg_right.add_bend(-angle, radius=radius - 2.2)
        wg_right.add_straight_segment(length=5, final_width=[0.1])

    if mc_type.find('u') != -1:
        print('u is selected')
        wg_right = Waveguide.make_at_port(Port((start_x + y2 - h * 2 + 5 * sin(2 * angle),
                                                start_y + mode_converter_params['guide_length'] + mode_converter_params[
            'bending_length'] - x2 - 5 * cos(2 * angle)),
                                               angle=pi / 2 + 2 * angle, width=0.1))
        wg_right.add_straight_segment(length=5, final_width=mode_converter_params['bot_wg_width'])
        wg_right.add_bend(-angle, radius=radius - 2.2)
        wg_right.add_bend(-angle, radius=radius - 2.2)
        wg_right.add_straight_segment(length=mode_converter_params['cpl_length'])
        wg_right.add_bend(-angle, radius=radius)
        wg_right.add_bend(+angle, radius=radius)
        wg_right.add_straight_segment(length=mode_converter_params['guide_length'])

    if mc_type.find('r') != -1:
        wg_bot = Waveguide.make_at_port(Port((start_x + mode_converter_params['guide_length'] + mode_converter_params['bending_length']-x2-5*cos(2 * angle),
                                              start_y-y2+h*2-5*sin(2*angle)),
                                             angle=2 * angle, width=0.1))
        wg_bot.add_straight_segment(length=5, final_width=mode_converter_params['bot_wg_width'])
        wg_bot.add_bend(-angle, radius=radius - 2.2)
        wg_bot.add_bend(-angle, radius=radius - 2.2)
        wg_bot.add_straight_segment(length=mode_converter_params['cpl_length'])
        wg_bot.add_bend(-angle, radius=radius)
        wg_bot.add_bend(+angle, radius=radius)
        wg_bot.add_straight_segment(length=mode_converter_params['guide_length'])

    if (mc_type.find('l') != -1) or (mc_type.find('r') != -1):
        wg_top = Waveguide.make_at_port(Port((start_x, start_y + mode_converter_params['bending_height']
                                          + mode_converter_params['gap'] / 2
                                          + mode_converter_params['top_wg_width'] / 2),
                                         angle=0,
                                         width=mode_converter_params['top_wg_width']))
        wg_top.add_straight_segment(length=2 * mode_converter_params['guide_length'] +
                                2 * mode_converter_params['bending_length'] +
                                mode_converter_params['cpl_length'])
        cell_name.add_to_layer(layer, wg_bot, wg_top)

    if (mc_type.find('u') != -1) or (mc_type.find('d') != -1):
        wg_left = Waveguide.make_at_port(Port((start_x - mode_converter_params['bending_height']
                                          - mode_converter_params['gap'] / 2
                                          - mode_converter_params['top_wg_width'] / 2,
                                              start_y ),
                                         angle=pi/2,
                                         width=mode_converter_params['top_wg_width']))
        wg_left.add_straight_segment(length=2 * mode_converter_params['guide_length'] +
                                2 * mode_converter_params['bending_length'] +
                                mode_converter_params['cpl_length'])
        cell_name.add_to_layer(layer, wg_left, wg_right)
    return cell_name

def generate_frame(x_len, y_len, frame_width=1, frame_mark_dist=100, layer=[1, 2, 3, 4], mark_len=50, mark_width=3):
    cell = Cell('Frame')
    frame_x_len = x_len
    frame_y_len = y_len

    trench(center_x=frame_x_len/2, center_y=frame_width/2, length=frame_x_len, width=frame_width, layer=1, cell_name=cell)
    trench(center_x=frame_width/2, center_y=frame_y_len/2, length=frame_width, width=frame_y_len, layer=1, cell_name=cell)
    trench(center_x=frame_x_len/2, center_y=frame_y_len-frame_width/2, length=frame_x_len, width=frame_width, layer=1, cell_name=cell)
    trench(center_x=frame_x_len-frame_width/2, center_y=frame_y_len/2, length=frame_width, width=frame_y_len, layer=1, cell_name=cell)

    local_mark_params = {
        'length': mark_len,
        'width': mark_width,
    }
    central_mark_params = {
        'length': mark_len*1.5,
        'width': mark_width,
    }

    cell = local_mark(frame_mark_dist, frame_mark_dist, local_mark_params, 1, cell)
    cell = local_mark(frame_mark_dist, y_len/2, local_mark_params, 1, cell)
    cell = local_mark(frame_mark_dist, y_len-frame_mark_dist, local_mark_params, 1, cell)
    cell = local_mark(x_len-frame_mark_dist, frame_mark_dist, local_mark_params, 1, cell)
    cell = local_mark(x_len-frame_mark_dist, y_len/2, local_mark_params, 1, cell)
    cell = local_mark(x_len-frame_mark_dist, y_len-frame_mark_dist, local_mark_params, 1, cell)
    cell = local_mark(x_len/2, frame_mark_dist, local_mark_params, 1, cell)
    # cell = local_mark(x_len/2, y_len/2, local_mark_params, 1, cell)
    cell = local_mark(x_len/2, y_len-frame_mark_dist, local_mark_params, 1, cell)

    ###central mark!!!
    cell = local_mark(x_len/2, y_len/2, central_mark_params, 1, cell)
    ###intermediate marks
    cell = local_mark(frame_mark_dist, y_len/4*1, local_mark_params, 1, cell)
    cell = local_mark(frame_mark_dist, y_len/4*3, local_mark_params, 1, cell)
    
    cell = local_mark(x_len-frame_mark_dist, y_len/4*1, local_mark_params, 1, cell)
    cell = local_mark(x_len-frame_mark_dist, y_len/4*3, local_mark_params, 1, cell)

    cell = local_mark(x_len/4*1, frame_mark_dist, local_mark_params, 1, cell)
    cell = local_mark(x_len/4*3, frame_mark_dist, local_mark_params, 1, cell)

    cell = local_mark(x_len/4*1, y_len-frame_mark_dist, local_mark_params, 1, cell)
    cell = local_mark(x_len/4*3, y_len-frame_mark_dist, local_mark_params, 1, cell)

    ###intermediate marks
    cell = local_mark(x_len/4*1, y_len/2, local_mark_params, 1, cell)
    cell = local_mark(x_len/4*3, y_len/2, local_mark_params, 1, cell)

    for l in layer:
        if l==1:
            continue
        cell.add_to_layer(l, rectangular_xywh(center_x=25, center_y=25, length=50, width=50))
        cell.add_to_layer(l, rectangular_xywh(center_x=25, center_y=y_len-25, length=50, width=50))
        cell.add_to_layer(l, rectangular_xywh(center_x=x_len-25, center_y=25, length=50, width=50))
        cell.add_to_layer(l, rectangular_xywh(center_x=x_len-25, center_y=y_len-25, length=50, width=50))
    return cell
# def mode_converter(start_x, start_y, mode_converter_params, mc_type, layer, cell_name):    # mc type 'l--left r--right'
#     h = (mode_converter_params['bending_height'] - mode_converter_params['gap'] / 2 -
#          mode_converter_params['bot_wg_width'] / 2) / 2
#     radius = (h ** 2 + mode_converter_params['bending_length'] ** 2 / 4) / (2 * h)
#     angle = asin(mode_converter_params['bending_length'] / (2 * radius))
#     d = mode_converter_params['bending_length'] / 2 - h / sin(2 * angle) - h / tan(2 * angle)
#     x = 2 * d * sin(angle) ** 2
#     y = x / tan(angle)
#     y2=(radius-2.2)*(1-cos(2*angle))
#     x2=(radius-2.2)*sin(2*angle)

#     wg_bot = None

#     if mc_type.find('l') != -1:
#         print('converter l')
#         wg_bot = Waveguide.make_at_port(Port((start_x, start_y),
#                                              angle=0, width=mode_converter_params['bot_wg_width']))
#         wg_bot.add_straight_segment(length=mode_converter_params['guide_length'])
#         wg_bot.add_bend(angle, radius=radius)
#         wg_bot.add_bend(-angle, radius=radius)
#         wg_bot.add_straight_segment(length=mode_converter_params['cpl_length'])
#         # wg_bot.add_bend(-angle, radius=radius - 2.2)
#         # wg_bot.add_bend(-angle, radius=radius - 2.2)
#         wg_bot.add_straight_segment(length=5, final_width=[0.1])

#     if mc_type.find('r') != -1:
#         print('converter r')
#         wg_bot = Waveguide.make_at_port(Port((start_x + mode_converter_params['guide_length'] + mode_converter_params['bending_length']-x2-5*cos(2 * angle),
#                                               start_y-y2+h*2-5*sin(2*angle)),
#                                              angle=2 * angle, width=0.1))
#         wg_bot.add_straight_segment(length=5, final_width=mode_converter_params['bot_wg_width'])
#         wg_bot.add_bend(-angle, radius=radius - 2.2)
#         wg_bot.add_bend(-angle, radius=radius - 2.2)
#         wg_bot.add_straight_segment(length=     ['cpl_length'])
#         wg_bot.add_bend(-angle, radius=radius)
#         wg_bot.add_bend(+angle, radius=radius)
#         wg_bot.add_straight_segment(length=mode_converter_params['guide_length'])

#     if mc_type.find('d') != -1:
#         wg_right = Waveguide.make_at_port(Port((start_x, start_y),
#                                              angle=pi/2, width=mode_converter_params['bot_wg_width']))
#         wg_right.add_straight_segment(length=mode_converter_params['guide_length'])
#         wg_right.add_bend(angle, radius=radius)
#         wg_right.add_bend(-angle, radius=radius)
#         wg_right.add_straight_segment(length=mode_converter_params['cpl_length'])
#         wg_right.add_bend(-angle, radius=radius - 2.2)
#         wg_right.add_bend(-angle, radius=radius - 2.2)
#         wg_right.add_straight_segment(length=5, final_width=[0.1])

#     if mc_type.find('u') != -1:
#         wg_right = Waveguide.make_at_port(Port((start_x + y2 - h * 2 + 5 * sin(2 * angle),
#                                                 start_y + mode_converter_params['guide_length'] + mode_converter_params[
#             'bending_length'] - x2 - 5 * cos(2 * angle)),
#                                                angle=pi / 2 + 2 * angle, width=0.1))
#         wg_right.add_straight_segment(length=5, final_width=mode_converter_params['bot_wg_width'])
#         wg_right.add_bend(-angle, radius=radius - 2.2)
#         wg_right.add_bend(-angle, radius=radius - 2.2)
#         wg_right.add_straight_segment(length=mode_converter_params['cpl_length'])
#         wg_right.add_bend(-angle, radius=radius)
#         wg_right.add_bend(+angle, radius=radius)
#         wg_right.add_straight_segment(length=mode_converter_params['guide_length'])


#     wg_top = Waveguide.make_at_port(Port((start_x, start_y + mode_converter_params['bending_height']
#                                           + mode_converter_params['gap'] / 2
#                                           + mode_converter_params['top_wg_width'] / 2),
#                                          angle=0,
#                                          width=mode_converter_params['top_wg_width']))
#     wg_top.add_straight_segment(length=2 * mode_converter_params['guide_length'] +
#                                 2 * mode_converter_params['bending_length'] +
#                                 mode_converter_params['cpl_length'])

#     cell_name.add_to_layer(layer, wg_top)
#     return cell_name

