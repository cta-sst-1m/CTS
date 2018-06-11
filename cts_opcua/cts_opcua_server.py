import logging
import sys
import os
import time

from opcua.ua.uatypes import NodeId
from opcua import ua, uamethod, Server
import numpy as np
import json

import cts_core.cameratestsetup as camtestsetup
import cts_can.cts_can as com


try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


class CTSServer:
    """
    CTSClient class is the OpcUa client for the CTS OpcUa server.
    It also contains various high level function allowing to turn on and off
    leds, run scans, display the CTS status, load MC events in the CTS, etc...
    Input:
        - angle_cts : the configuration of the CTS (0., 120. or 240. degrees )
    """

    def __init__(self, angle_cts):
        """
        Initialise function for CTSClient
        Input:
            - angle_cts : the configuration of the CTS
            (0., 120. or 240. degrees)
        """
        self.server = Server()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        angle_str = str(int(angle_cts))
        self.cts = camtestsetup.CTS(
            current_dir + '/../config/cts_config_' + angle_str + '.cfg',
            current_dir + '/../config/camera_config.cfg',
            angle=angle_cts, connected=True
        )
        com.initialise_can(self.cts)
        # optional: setup logging
        logging.basicConfig(level=logging.WARN)
        self.logger = logging.getLogger("opcua.address_space")
        self.logger.setLevel(logging.DEBUG)
        self.server.set_endpoint("opc.tcp://0.0.0.0:4843" +
                                 "/cameratestsetup/server/")
        self.server.set_server_name("Camera Test Setup OpcUa Server")
        # get Objects node, this is where we should put our custom stuff
        self.objects = self.server.get_objects_node()
        # create the ua structure
        create_opcua_structure(self.cts, self.objects)
        # starting!
        self.server.start()


def mod2r(m):
    return (m + 1 & 0b1111111) | (0b1101 << 7)


def element_to_array(val):
    if not isinstance(val, list):
        return [val]
    else:
        return val


def arg_general(_name, _desc, _type, array_dim=None):
    if array_dim is None:
        array_dim = []
    arg = ua.Argument()
    arg.Name = _name
    arg.DataType = ua.NodeId(_type)
    arg.ArrayDimensions = []
    arg.Description = ua.LocalizedText(_desc)
    arg.ValueRank = -1
    arg.ArrayDimensions = array_dim
    return arg


def arg_int(name, desc, array_dim=None):
    return arg_general(name, desc, ua.ObjectIds.Int64, array_dim=array_dim)


def arg_bool(name, desc, array_dim=None):
    return arg_general(name, desc, ua.ObjectIds.Boolean, array_dim=array_dim)


def arg_double(name, desc, array_dim=None):
    return arg_general(name, desc, ua.ObjectIds.Double, array_dim=array_dim)


def arg_string(name, desc, array_dim=None):
    return arg_general(name, desc, ua.ObjectIds.String, array_dim=array_dim)


def arg_float(name, desc, array_dim=None):
    return arg_general(name, desc, ua.ObjectIds.Float, array_dim=array_dim)


def create_opcua_structure(_cts, _parent_node):
    """
    Populating the OPC adress space
    """
    create_opcua_variables(_cts, _parent_node)
    create_opcua_mapping(_cts)
    create_opcua_functions(_cts)


def create_opcua_variables(_cts, _parent_node):
    setattr(_cts,
            'main_folder', _parent_node.add_folder(NodeId('CTS', 2), "CTS"))
    setattr(_cts,
            'time', _cts.main_folder.add_variable(NodeId('CTS.time', 2),
                                                  "time", int(time.time())))
    setattr(_cts,
            'DAC', _cts.main_folder.add_folder(NodeId('CTS.DAC', 2), "DAC"))
    setattr(_cts,
            'DAC_AC', _cts.DAC.add_folder(NodeId('CTS.DAC.AC', 2), "AC"))
    setattr(_cts,
            'DAC_DC', _cts.DAC.add_folder(NodeId('CTS.DAC.DC', 2), "DC"))
    setattr(_cts, 'DACoffset',
            _cts.main_folder.add_folder(NodeId('CTS.DACoffset', 2),
                                        "DACoffset"))
    setattr(_cts, 'DACoffset_AC',
            _cts.DACoffset.add_folder(NodeId('CTS.DACoffset.AC', 2), "AC"))
    setattr(_cts, 'DACoffset_DC',
            _cts.DACoffset.add_folder(NodeId('CTS.DACoffset.DC', 2), "DC"))
    setattr(_cts,
            'status', _cts.main_folder.add_folder(NodeId('CTS.status', 2),
                                                  "status"))
    setattr(_cts, 'status_AC',
            _cts.status.add_folder(NodeId('CTS.status.AC', 2), "AC"))
    setattr(_cts, 'status_DC',
            _cts.status.add_folder(NodeId('CTS.status.DC', 2), "DC"))
    setattr(
        _cts,
        'patches_AC_DAC',
        _cts.DAC_AC.add_variable(
            NodeId('CTS.DAC.AC.patches', 2),
            "patches",
            np.zeros([432, ], dtype=np.int32).tolist()
        )
    )
    setattr(
        _cts,
        'boards_DC_DAC',
        _cts.DAC_DC.add_variable(
            NodeId('CTS.DAC.DC.boards', 2),
            "boards",
            np.zeros([27, ], dtype=np.int32).tolist()
        )
    )
    setattr(
        _cts,
        'patches_AC_offset',
        _cts.DACoffset_AC.add_variable(
            NodeId('CTS.DACoffset.AC.patches', 2),
            "patches",
            np.zeros([432, ], dtype=np.int32).tolist()
        )
    )
    setattr(
        _cts,
        'boards_DC_offset',
        _cts.DACoffset_DC.add_variable(
            NodeId('CTS.DACoffset.DC.boards', 2),
            "boards",
            np.zeros([27, ], dtype=np.int32).tolist()
        )
    )
    setattr(
        _cts,
        'pixels_AC_status',
        _cts.status_AC.add_variable(
            NodeId('CTS.status.AC.pixels', 2),
            "status",
            np.zeros([1296, ], dtype=bool).tolist()
        )
    )
    setattr(
        _cts,
        'pixels_DC_status',
        _cts.status_DC.add_variable(
            NodeId('CTS.status.DC.pixels', 2),
            "status",
            np.zeros([1296, ], dtype=bool).tolist()
        )
    )


def create_opcua_mapping(_cts):
    # mapping
    setattr(
        _cts,
        'mapping',
        _cts.main_folder.add_folder(NodeId('CTS.mapping', 2), "mapping")
    )
    pixels_to_patches = np.zeros([1296, ], dtype=np.int32)
    # 423 patches * 3 LEDs each
    patches_to_pixels = np.zeros([432, 3], dtype=np.int32)
    pixels_to_halfBoards = np.zeros([1296, ], dtype=np.int32)
    # 54 half boards * 24 LEDs each
    halfBoards_to_pixels = np.zeros([54, 24], dtype=np.int32)
    pixels_to_boards = np.zeros([1296, ], dtype=np.int32)
    # 27 boards * 48 LEDs each
    boards_to_pixels = np.zeros([27, 48], dtype=np.int32)
    patches_to_halfBoards = np.zeros([432, ], dtype=np.int32)
    # 54 half boards * 8 patches each
    halfBoards_to_patches = np.zeros([54, 8], dtype=np.int32)
    for led in _cts.LEDs:
        pixel = led.camera_pixel_id
        patch = led.led_patch
        id_in_led_patch = led.id_in_led_patch
        board = led.led_board
        id_in_led_board = led.id_in_led_board
        halfBoard = 2 * board + int(np.floor(id_in_led_board / 24))
        id_in_halfBoard = id_in_led_board % 24
        patchId_in_halfBoard = int(np.floor(id_in_halfBoard / 3))
        pixels_to_patches[pixel] = patch
        patches_to_pixels[patch, id_in_led_patch] = pixel
        pixels_to_halfBoards[pixel] = halfBoard
        halfBoards_to_pixels[halfBoard, id_in_halfBoard] = pixel
        pixels_to_boards[pixel] = board
        boards_to_pixels[board, id_in_led_board] = pixel
        patches_to_halfBoards[patch] = halfBoard
        halfBoards_to_patches[halfBoard, patchId_in_halfBoard] = patch
    setattr(
        _cts,
        'pixels_to_patches',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.pixels_to_patches', 2),
            "pixels_to_patches",
            pixels_to_patches.tolist()
        )
    )
    setattr(
        _cts,
        'patches_to_pixels',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.patches_to_pixels', 2),
            "patches_to_pixels",
            patches_to_pixels.tolist()
        )
    )
    setattr(
        _cts,
        'pixels_to_halfBoards',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.pixels_to_halfBoards', 2),
            "pixels_to_halfBoards",
            pixels_to_halfBoards.tolist()
        )
    )
    setattr(
        _cts,
        'halfBoards_to_pixels',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.halfBoards_to_pixels', 2),
            "halfBoards_to_pixels",
            halfBoards_to_pixels.tolist()
        )
    )
    setattr(
        _cts,
        'pixels_to_boards',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.pixels_to_boards', 2),
            "pixels_to_boards",
            pixels_to_boards.tolist()
        )
    )
    setattr(
        _cts,
        'boards_to_pixels',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.boards_to_pixels', 2),
            "boards_to_pixels",
            boards_to_pixels.tolist()
        )
    )
    setattr(
        _cts,
        'patches_to_halfBoards',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.patches_to_halfBoards', 2),
            "patches_to_halfBoards",
            patches_to_halfBoards.tolist()
        )
    )
    setattr(
        _cts,
        'halfBoards_to_patches',
        _cts.mapping.add_variable(
            NodeId('CTS.mapping.halfBoards_to_patches', 2),
            "halfBoards_to_patches",
            halfBoards_to_patches.tolist()
        )
    )


def create_opcua_functions(_cts):
    # Functions' parameters
    board = arg_int("Board", "LED Board id")
    halfBoard = arg_int("Half-board", "LED Half-Board id")
    patch = arg_int("Patch", "LED Patch id")
    level_dc = arg_int("DC DAC level", "level for DC led: int")
    level_ac = arg_int("AC DAC level", "level for AC led: int")
    offset_dc = arg_int("DC DAC offset", "offset for DC led: int")
    offset_ac = arg_int("AC DAC offset", "offset for AC led: int")
    halfBoard_status = arg_int(
        "Pixels's status of an 1/2 board (int)",
        "0x000000 (24 leds off) to 0xffffff (24 leds on)"
    )
    pixel_status = arg_bool(
        "Pixel status for all DC and AC LEDs", "0: OFF, 1: ON"
    )
    pixels_ac_status = arg_string("pixels's AC statuses (JSON)",
                                  "1296 x [Status: True(1) or False(0)]")
    pixels_dc_status = arg_string("pixels's DC statuses (JSON)",
                                  "1296 x [Status: True(1) or False(0)]")
    patches_level = arg_string("Patches's AC DAC levels (JSON)",
                               "432 x [DAC level: int]")
    patches_offset = arg_string("Patches's AC DAC offsets (JSON)",
                                "432 x [DAC offset: int]")
    boards_level = arg_string("Boards's DC DAC levels (JSON)",
                              "27 x [DAC level: int]")
    boards_offset = arg_string("Boards's DC DAC offsets (JSON)",
                               "27 x [DAC offset: int]")
    pixels_level = arg_string("Pixels's DAC levels (JSON)",
                              "1296 x [DAC level: int]")
    pixels_offset = arg_string("Pixels's DAC offsets (JSON)",
                               "1296 x [DAC offsets: int]")
    outarg = arg_string("Result", "Result")
    # Now add the functions.
    setattr(
        _cts,
        'set_board_DC_DAC',
        _cts.DAC_DC.add_method(
            NodeId('CTS.DAC.DC.set_board', 2),
            'set_board',
            set_board_DC_DAC,
            [board, level_dc],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_patch_AC_DAC',
        _cts.DAC_AC.add_method(
            NodeId('CTS.DAC.AC.set_patch', 2),
            'set_patch',
            set_patch_AC_DAC,
            [patch, level_ac],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_board_DC_offset',
        _cts.DACoffset_DC.add_method(
            NodeId('CTS.DACOffset.DC.set_board', 2),
            'set_board',
            set_board_DC_offset,
            [board, offset_dc],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_patch_AC_offset',
        _cts.DACoffset_AC.add_method(
            NodeId('CTS.DACoffset.AC.set_patch', 2),
            'set_patch',
            set_patch_AC_offset,
            [patch, offset_ac],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_halfBoard_AC_DAC',
        _cts.DAC_AC.add_method(
            NodeId('CTS.DAC.AC.set_halfBoard', 2),
            'set_halfBoard',
            set_halfBoard_AC_DAC,
            [halfBoard, level_ac],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_halfBoard_AC_offset',
        _cts.DACoffset_AC.add_method(
            NodeId('CTS.DACoffset.AC.set_halfBoard', 2),
            'set_halfBoard',
            set_halfBoard_AC_offset,
            [halfBoard, offset_ac],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_leds_AC_in_halfBoard_status',
        _cts.status_AC.add_method(
            NodeId('CTS.status.AC.set_leds_in_halfBoard', 2),
            'set_leds_in_halfBoard',
            set_leds_AC_in_halfBoard_status,
            [halfBoard, halfBoard_status],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_leds_DC_in_halfBoard_status',
        _cts.status_DC.add_method(
            NodeId('CTS.status.DC.set_leds_in_halfBoard', 2),
            'set_leds_in_halfBoard',
            set_leds_DC_in_halfBoard_status,
            [halfBoard, halfBoard_status],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_patches_AC_DAC',
        _cts.DAC_AC.add_method(
            NodeId('CTS.DAC.AC.set_patches', 2),
            'set_patches',
            set_patches_AC_DAC,
            [patches_level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_boards_DC_DAC',
        _cts.DAC_DC.add_method(
            NodeId('CTS.DAC.DC.set_boards', 2),
            'set_boards',
            set_boards_DC_DAC,
            [boards_level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_patches_AC_offset',
        _cts.DACoffset_AC.add_method(
            NodeId('CTS.DACoffset.AC.set_patches', 2),
            'set_patches',
            set_patches_AC_offset,
            [patches_offset],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_boards_DC_offset',
        _cts.DACoffset_DC.add_method(
            NodeId('CTS.DACoffset.DC.set_boards', 2),
            'set_boards',
            set_boards_DC_offset,
            [boards_offset],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_all_DAC',
        _cts.DAC.add_method(
            NodeId('CTS.DAC.set_all', 2),
            'set_all',
            set_all_DAC,
            [level_dc, level_ac],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_all_offset',
        _cts.DACoffset.add_method(
            NodeId('CTS.DACoffset.set_all', 2),
            'set_all',
            set_all_offset,
            [offset_dc, offset_ac],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_dc_status',
        _cts.status_DC.add_method(
            NodeId('CTS.status.DC.set_pixels', 2),
            'set_pixels',
            set_pixels_dc_status,
            [pixels_dc_status],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_ac_status',
        _cts.status_AC.add_method(
            NodeId('CTS.status.AC.set_pixels', 2),
            'set_pixels',
            set_pixels_ac_status,
            [pixels_ac_status],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_ac_DAC',
        _cts.DAC_AC.add_method(
            NodeId('CTS.DAC.AC.set_pixels', 2),
            'set_pixels',
            set_pixels_ac_DAC,
            [pixels_level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_dc_DAC',
        _cts.DAC_DC.add_method(
            NodeId('CTS.DAC.DC.set_pixels', 2),
            'set_pixels',
            set_pixels_dc_DAC,
            [pixels_level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_ac_offset',
        _cts.DACoffset_AC.add_method(
            NodeId('CTS.DACoffset.AC.set_pixels', 2),
            'set_pixels',
            set_pixels_ac_offset,
            [pixels_offset],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_dc_offset',
        _cts.DACoffset_DC.add_method(
            NodeId('CTS.DACoffset.DC.set_pixels', 2),
            'set_pixels',
            set_pixels_dc_offset,
            [pixels_offset],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_pixels_dc_offset',
        _cts.DACoffset_DC.add_method(
            NodeId('CTS.DACoffset.DC.set_pixels', 2),
            'set_pixels',
            set_pixels_dc_offset,
            [pixels_offset],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_all_status',
        _cts.DACoffset_DC.add_method(
            NodeId('CTS.status.set_all_status', 2),
            'set_all',
            set_all_status,
            [pixels_offset],
            [outarg]
        )
    )
    print("opcua structure created")


ctsserver = None


"""
@uamethod
def update(parent):
    resdict = com.checkLEDStatus(ctsserver.cts.bus)
    modules_to_ac_leds = ctsserver.cts.status_modules_to_leds_intenal_id['AC']
    modules_to_dc_leds = ctsserver.cts.status_modules_to_leds_intenal_id['DC']
    for key, value in enumerate(resdict):
        _, mod = int(key.split('_',2))
        if mod in modules_to_ac_leds.keys():
            pass
        elif mod in modules_to_dc_leds.keys():
            pass
        else:
            print('WARNING in update(): wrong module "{}"'.format(mod))
"""


@uamethod
def set_patch_AC_DAC(parent, led_patch, level):
    level = int(level)
    led = ctsserver.cts.LED_patches[led_patch].LEDs[0]
    m = led.can_dac_module
    c = led.can_dac_channel
    # read all AC DAC levels
    levels = ctsserver.cts.patches_AC_DAC.get_value()
    # update and set
    levels[led_patch] = level
    ctsserver.cts.patches_AC_DAC.set_value(levels)
    com.setDACLevel(ctsserver.cts.bus, level, module=m, channel=c)
    return 'done setting lvl=' + str(level) + ' to patch ' + str(led_patch)


@uamethod
def set_patch_AC_offset(parent, led_patch, offset):
    offset = int(offset)
    led = ctsserver.cts.LED_patches[led_patch].LEDs[0]
    m = led.can_dac_module
    c = led.can_dac_channel
    # read all AC DAC offsets
    offsets = ctsserver.cts.patches_AC_offset.get_value()
    # update and set
    offsets[led_patch] = offset
    ctsserver.cts.patches_AC_offset.set_value(offsets)
    com.setDACOffset(ctsserver.cts.bus, offset, module=m, channel=c)
    return 'done setting offset=' + str(offset) + ' to patch ' + str(led_patch)


@uamethod
def set_board_DC_DAC(parent, board, level):
    level = int(level)
    m = ctsserver.cts.LED_boards[board].LEDs[0].can_dac_module
    c = ctsserver.cts.LED_boards[board].LEDs[0].can_dac_channel
    com.setDACLevel(ctsserver.cts.bus, level, module=m, channel=c)
    levels = ctsserver.cts.boards_DC_DAC.get_value()
    levels[board] = level
    ctsserver.cts.boards_DC_DAC.set_value(levels)
    return 'done setting DC level=' + str(level) + ' to board ' + str(board)


@uamethod
def set_board_DC_offset(parent, board, offset):
    offset = int(offset)
    m = ctsserver.cts.LED_boards[board].LEDs[0].can_dac_module
    c = ctsserver.cts.LED_boards[board].LEDs[0].can_dac_channel
    com.setDACOffset(ctsserver.cts.bus, offset, module=m, channel=c)
    offsets = ctsserver.cts.boards_DC_offset.get_value()
    offsets[board] = offset
    ctsserver.cts.boards_DC_offset.set_value(offsets)
    return 'done setting DC offset=' + str(offset) + ' to board ' + str(board)


@uamethod
def set_halfBoard_AC_DAC(parent, halfBoard, level):
    level = int(level)
    halfBoards_to_patches = ctsserver.cts.halfBoards_to_patches.get_value()
    patches = halfBoards_to_patches[halfBoard]
    m = ctsserver.cts.LED_patches[patches[0]].LEDs[0].can_dac_module
    com.setDACLevel(ctsserver.cts.bus, level, module=m, channel=8)
    levels = ctsserver.cts.patches_AC_DAC.get_value()
    for patch in patches:
        levels[patch] = level
    ctsserver.cts.patches_AC_DAC.set_value(levels)
    return 'done setting AC level=' + str(level) + ' to half board ' + \
           str(halfBoard)


@uamethod
def set_halfBoard_AC_offset(parent, halfBoard, offset):
    offset = int(offset)
    halfBoards_to_patches = ctsserver.cts.halfBoards_to_patches.get_value()
    patches = halfBoards_to_patches[halfBoard]
    m = ctsserver.cts.LED_patches[patches[0]].LEDs[0].can_dac_module
    com.setDACOffset(ctsserver.cts.bus, offset, module=m, channel=8)
    offsets = ctsserver.cts.patches_AC_offset.get_value()
    for patch in patches:
        offsets[patch] = offset
    ctsserver.cts.patches_AC_offset.set_value(offsets)
    return 'done setting AC offset=' + str(offset) + ' to half board ' + \
           str(halfBoard)


@uamethod
def set_leds_AC_in_halfBoard_status(parent, halfBoard,
                                    halfBoard_status=0xffffff):
    halfBoard_status = int(halfBoard_status)
    halfBoards_to_pixels = ctsserver.cts.halfBoards_to_pixels.get_value()
    pixels = halfBoards_to_pixels[halfBoard]
    led = ctsserver.cts.pixel_to_led['AC'][pixels[0]]
    m = ctsserver.cts.LEDs[led].can_status_module
    com.setLED(ctsserver.cts.bus,
               module=m, led_mask=halfBoard_status, globalCmd=1)
    halfBoards_to_pixels = ctsserver.cts.halfBoards_to_pixels.get_value()
    pixels = halfBoards_to_pixels[halfBoard]
    pixels_AC_status = ctsserver.cts.pixels_AC_status.get_value()
    for pixel in pixels:
        led = ctsserver.cts.pixel_to_led['AC'][pixel]
        led_in_halfBoard = ctsserver.cts.LEDs[led].can_status_channel
        status = (halfBoard_status & (1 << (led_in_halfBoard))) > 0
        pixels_AC_status[pixel] = status
    ctsserver.cts.pixels_AC_status.set_value(pixels_AC_status)
    return "done setting AC LEDs status to {0:b}".format(halfBoard_status) + \
           " for 1/2 board {}".format(halfBoard)


@uamethod
def set_leds_DC_in_halfBoard_status(parent, halfBoard,
                                    halfBoard_status=0xffffff):
    halfBoard_status = int(halfBoard_status)
    halfBoards_to_pixels = ctsserver.cts.halfBoards_to_pixels.get_value()
    pixels = halfBoards_to_pixels[halfBoard]
    led = ctsserver.cts.pixel_to_led['DC'][pixels[0]]
    m = ctsserver.cts.LEDs[led].can_status_module
    com.setLED(ctsserver.cts.bus,
               module=m, led_mask=halfBoard_status, globalCmd=1)
    pixels_DC_status = ctsserver.cts.pixels_DC_status.get_value()
    for pixel in pixels:
        led = ctsserver.cts.pixel_to_led['DC'][pixel]
        led_in_halfBoard = ctsserver.cts.LEDs[led].can_status_channel
        status = (halfBoard_status & (1 << (led_in_halfBoard))) > 0
        pixels_DC_status[pixel] = status
    ctsserver.cts.pixels_DC_status.set_value(pixels_DC_status)
    return "done setting DC LEDs status to {0:b}".format(halfBoard_status) + \
           " for 1/2 board {}".format(halfBoard)


@uamethod
def set_patches_AC_DAC(parent, patches_level):
    patches_level = json.loads(patches_level)
    if len(patches_level) != 432:
        return 'ERROR: patches_level must be of shape (432,)'
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_patch_AC_DAC
    for patch, level in enumerate(patches_level):
        base.call_method(method, patch, int(level))
    return 'done setting individual AC levels for all patches'


@uamethod
def set_patches_AC_offset(parent, patches_offset):
    patches_offset = json.loads(patches_offset)
    if len(patches_offset) != 432:
        return 'ERROR: patches_offset must be of shape (432,)'
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_patch_AC_offset
    for patch, offset in enumerate(patches_offset):
        base.call_method(method, patch, int(offset))
    return 'done setting individual AC offsets for all patches'


@uamethod
def set_halfBoards_AC_DAC(parent, halfBoards_level):
    halfBoards_level = json.loads(halfBoards_level)
    if len(halfBoards_level) != 54:
        return 'ERROR: halfBoards_level must be of shape (54,)'
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_halfBoard_AC_DAC
    for halfBoard, level in enumerate(halfBoards_level):
        base.call_method(method, halfBoard, int(level))
    return 'done setting individual AC levels for all half-boards'


@uamethod
def set_halfBoards_AC_offset(parent, halfBoards_offset):
    halfBoards_offset = json.loads(halfBoards_offset)
    if len(halfBoards_offset) != 54:
        return 'ERROR: halfBoards_offset must be of shape (54,)'
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_halfBoard_AC_offset
    for halfBoard, offset in enumerate(halfBoards_offset):
        base.call_method(method, halfBoard, int(offset))
    return 'done setting individual AC offsets for all half-boards'


@uamethod
def set_boards_DC_DAC(parent, boards_level):
    boards_level = json.loads(boards_level)
    if len(boards_level) != 27:
        return 'ERROR: boards_level must be of shape (27,)'
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_board_DC_DAC
    for board, level in enumerate(boards_level):
        base.call_method(method, board, int(level))
    return 'done setting individual DC levels for all boards'


@uamethod
def set_boards_DC_offset(parent, boards_offset):
    boards_offset = json.loads(boards_offset)
    if len(boards_offset) != 27:
        return 'ERROR: boards_offset must be of shape (27,)'
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_board_DC_offset
    for board, offset in enumerate(boards_offset):
        base.call_method(method, board, int(offset))
    return 'done setting individual DC offsets for all boards'


@uamethod
def set_all_DAC(parent, level_dc, level_ac):
    level_dc = int(level_dc)
    level_ac = int(level_ac)
    # Setting all modules, only channel 0 to level_dc
    # CAUTION: channel 0 of AC set as well
    com.setDACLevel(ctsserver.cts.bus, level_dc, channel=0, module=None)
    ctsserver.cts.boards_DC_DAC.set_value(
        (level_dc * np.ones([27, ], dtype=int)).tolist()
    )
    # Setting all modules, channel 8 to level_ac
    # channel 8 (meaning all channels) only valid fo ac, so only ac get set.
    com.setDACLevel(ctsserver.cts.bus, level_ac, channel=8, module=None)
    ctsserver.cts.patches_AC_DAC.set_value(
        (level_ac * np.ones([432, ], dtype=int)).tolist()
    )
    return 'done setting DC and AC levels (boadcast)'


@uamethod
def set_all_offset(parent, offset_dc, offset_ac):
    offset_dc = int(offset_dc)
    offset_ac = int(offset_ac)
    # Setting all modules, only channel 0 to offset_dc
    # CAUTION: channel 0 of AC set as well
    com.setDACOffset(ctsserver.cts.bus, offset_dc, channel=0, module=None)
    ctsserver.cts.boards_DC_offset.set_value(
        (offset_dc * np.ones([27, ], dtype=int)).tolist()
    )
    # Setting all modules, channel 8 to offset_ac
    # channel 8 (meaning all channels) only valid fo ac, so only ac get set.
    com.setDACOffset(ctsserver.cts.bus, offset_ac, channel=8, module=None)
    ctsserver.cts.patches_AC_offset.set_value(
        (offset_ac * np.ones([432, ], dtype=int)).tolist()
    )
    return 'done setting DC and AC offsets (boadcast)'


@uamethod
def set_pixels_dc_status(parent, pixels_dc_status):
    pixels_dc_status = json.loads(pixels_dc_status)
    if len(pixels_dc_status) != 1296:
        return 'ERROR: halfBoards_status must be of shape (1296,)'
    halfBoards_to_pixels = ctsserver.cts.halfBoards_to_pixels.get_value()
    n_halfBoard = len(halfBoards_to_pixels)
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_leds_DC_in_halfBoard_status
    for halfBoard in range(n_halfBoard):
        pixels = halfBoards_to_pixels[halfBoard]
        halfBoard_status = 0
        for pixel in pixels:
            status = pixels_dc_status[pixel]
            led = ctsserver.cts.pixel_to_led['DC'][pixel]
            led_in_halfBoard = ctsserver.cts.LEDs[led].can_status_channel
            halfBoard_status |= (status << led_in_halfBoard)
        base.call_method(method, halfBoard, halfBoard_status)
    return 'done setting individual DC status for all half-boards'


@uamethod
def set_pixels_ac_status(parent, pixels_ac_status):
    pixels_ac_status = json.loads(pixels_ac_status)
    if len(pixels_ac_status) != 1296:
        return 'ERROR: status of AC pixels must be of shape (1296,)'
    halfBoards_to_pixels = ctsserver.cts.halfBoards_to_pixels.get_value()
    n_halfBoard = len(halfBoards_to_pixels)
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_leds_AC_in_halfBoard_status
    for halfBoard in range(n_halfBoard):
        pixels = halfBoards_to_pixels[halfBoard]
        halfBoard_status = 0
        for pixel in pixels:
            status = pixels_ac_status[pixel]
            led = ctsserver.cts.pixel_to_led['AC'][pixel]
            led_in_halfBoard = ctsserver.cts.LEDs[led].can_status_channel
            halfBoard_status |= (status << led_in_halfBoard)
        base.call_method(method, halfBoard, halfBoard_status)
    return 'done setting individual AC status for all pixels'


@uamethod
def set_pixels_ac_DAC(parent, pixels_level):
    pixels_level = json.loads(pixels_level)
    if len(pixels_level) != 1296:
        return 'ERROR: DAC levels for AC pixels must be of shape (1296,)'
    halfBoards_to_patches = ctsserver.cts.halfBoards_to_patches.get_value()
    n_halfBoard = len(halfBoards_to_patches)
    patches_to_pixels = ctsserver.cts.patches_to_pixels.get_value()
    n_patch = len(patches_to_pixels)
    base = ctsserver.objects.get_child("0:CTS")
    method_patch = ctsserver.cts.set_patch_AC_DAC
    method_halfBoard = ctsserver.cts.set_halfBoard_AC_DAC
    for halfBoard in range(n_halfBoard):
        patches = halfBoards_to_patches[halfBoard]
        halfBoard_patches_levels = np.zeros([len(patches), ], dtype=float)
        for i, patch in enumerate(patches):
            pixels = patches_to_pixels[patch]
            assert len(pixels) == 3
            for pixel in pixels:
                halfBoard_patches_levels[i] += pixels_level[pixel] / 3
        halfBoard_patches_levels = np.array(np.round(halfBoard_patches_levels),
                                            dtype=int)
        if np.all(halfBoard_patches_levels == halfBoard_patches_levels[0]):
            base.call_method(method_halfBoard, halfBoard,
                             halfBoard_patches_levels[0])
        else:
            for i, patch in enumerate(patches):
                base.call_method(method_patch, patch,
                                 halfBoard_patches_levels[i])
    return 'done setting individual AC DAC level for all pixels'


@uamethod
def set_pixels_dc_DAC(parent, pixels_level):
    pixels_level = json.loads(pixels_level)
    if len(pixels_level) != 1296:
        return 'ERROR: DAC levels for DC pixels must be of shape (1296,)'
    boards_to_pixels = ctsserver.cts.boards_to_pixels.get_value()
    n_board = len(boards_to_pixels)
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_boards_DC_DAC
    boards_levels = np.zeros([n_board, ], dtype=float)
    for board in range(n_board):
        pixels = boards_to_pixels[board]
        assert len(pixels) == 48
        for pixel in pixels:
            boards_levels[board] += pixels_level[pixel] / 48
    boards_levels = np.array(np.round(boards_levels), dtype=int).tolist()
    base.call_method(method, json.dumps(boards_levels))
    return 'done setting individual DC DAC level for all pixels'


@uamethod
def set_pixels_ac_offset(parent, pixels_offset):
    pixels_offset = json.loads(pixels_offset)
    if len(pixels_offset) != 1296:
        return 'ERROR: DAC offset for AC pixels must be of shape (1296,)'
    halfBoards_to_patches = ctsserver.cts.halfBoards_to_patches.get_value()
    n_halfBoard = len(halfBoards_to_patches)
    patches_to_pixels = ctsserver.cts.patches_to_pixels.get_value()
    n_patch = len(patches_to_pixels)
    base = ctsserver.objects.get_child("0:CTS")
    method_patch = ctsserver.cts.set_patch_AC_offset
    method_halfBoard = ctsserver.cts.set_halfBoard_AC_offset
    for halfBoard in range(n_halfBoard):
        patches = halfBoards_to_patches[halfBoard]
        halfBoard_patches_offsets = np.zeros([len(patches), ], dtype=float)
        for i, patch in enumerate(patches):
            pixels = patches_to_pixels[patch]
            assert len(pixels) == 3
            for pixel in pixels:
                halfBoard_patches_offsets[i] += pixels_offset[pixel] / 3
        halfBoard_patches_offsets = np.array(np.round(
            halfBoard_patches_offsets), dtype=int)
        if np.all(halfBoard_patches_offsets == halfBoard_patches_offsets[0]):
            base.call_method(method_halfBoard, halfBoard,
                             halfBoard_patches_offsets[0])
        else:
            for i, patch in enumerate(patches):
                base.call_method(method_patch, patch,
                                 halfBoard_patches_offsets[i])
    return 'done setting individual AC DAC offset for all pixels'


@uamethod
def set_pixels_dc_offset(parent, pixels_offset):
    pixels_offset = json.loads(pixels_offset)
    if len(pixels_offset) != 1296:
        return 'ERROR: DAC offsets for DC pixels must be of shape (1296,)'
    boards_to_pixels = ctsserver.cts.boards_to_pixels.get_value()
    n_board = len(boards_to_pixels)
    base = ctsserver.objects.get_child("0:CTS")
    method = ctsserver.cts.set_boards_DC_offset
    boards_offsets = np.zeros([n_board, ], dtype=float)
    for board in range(n_board):
        pixels = boards_to_pixels[board]
        assert len(pixels) == 48
        for pixel in pixels:
            boards_offsets[board] += pixels_offset[pixel] / 48
    boards_offsets = np.array(np.round(boards_offsets), dtype=int).tolist()
    base.call_method(method, json.dumps(boards_offsets))
    return 'done setting individual DC DAC offset for all pixels'


@uamethod
def set_all_status(parent, status):
    status = bool(status)
    if status:
        led_mask = 0xffffff
    else:
        led_mask = 0x000000
    # Setting all modules
    com.setLED(ctsserver.cts.bus, led_mask=led_mask, globalCmd=True)
    statusses = (status * np.ones([1296, ], dtype=int)).tolist()
    ctsserver.cts.pixels_DC_status.set_value(statusses)
    ctsserver.cts.pixels_AC_status.set_value(statusses)
    return 'done setting status to {} for DC and AC LEDs'.format(status)


if __name__ == "__main__":
    angle = 0
    if len(sys.argv) > 1:
        angle = float(sys.argv[1])
    ctsserver = CTSServer(angle)
    ready = True
    print('---|> The server have been started')

    try:
        while True:
            time.sleep(0.5)
            if ready:
                ctsserver.cts.time.set_value(int(time.time()))
        embed()
    finally:
        ctsserver.server.stop()
