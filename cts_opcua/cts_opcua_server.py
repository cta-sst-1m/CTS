import logging
import sys
import os
import time

from opcua.ua.uatypes import NodeId
from opcua import ua, uamethod, Server

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
    '''
    CTSClient class is the OpcUa client for the CTS OpcUa server.

    It also contains various high level function allowing to turn on and off
    leds, run scans, display the CTS status, load MC events in the CTS, etc...

    Input:
        - angle_cts : the configuration of the CTS (0., 120. or 240. degrees )

    '''

    def __init__(self, angle_cts):
        '''
        Initialise function for CTSClient

        Input:
            - angle_cts : the configuration of the CTS
            (0., 120. or 240. degrees)

        '''

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

        # setup our own namespace
        # uri = "http://isdc.unige.ch/"
        # idx = self.server.register_namespace(uri)

        # get Objects node, this is where we should put our custom stuff
        self.objects = self.server.get_objects_node()

        # create the ua structure
        create_opcua_structure(self.cts, self.objects)

        # starting!
        ready = True
        self.server.start()


def mod2r(m):
    return (m + 1 & 0b1111111) | (0b1101 << 7)


def element_to_array(val):
    if not isinstance(val, list):
        return [val]
    else:
        return val


def arg_general(_name, _desc, _type):
    arg = ua.Argument()
    arg.Name = _name
    arg.DataType = ua.NodeId(_type)
    arg.ArrayDimensions = []
    arg.Description = ua.LocalizedText(_desc)
    arg.ValueRank = -1
    return arg


def arg_int(name, desc):
    return arg_general(name, desc, ua.ObjectIds.Int64)


def arg_bool(name, desc):
    return arg_general(name, desc, ua.ObjectIds.Boolean)


def arg_double(name, desc):
    return arg_general(name, desc, ua.ObjectIds.Double)


def arg_string(name, desc):
    return arg_general(name, desc, ua.ObjectIds.String)


def arg_float(name, desc):
    return arg_general(name, desc, ua.ObjectIds.Float)


def create_opcua_structure(_cts, _parent_node):
    '''
    Populating the OPC adress space
    '''
    setattr(_cts,
            'main_folder', _parent_node.add_folder(NodeId('CTS', 0), "CTS"))
    setattr(_cts,
            'time', _cts.main_folder.add_variable(NodeId('CTS.time', 1),
                                                  "time", int(time.time())))
    setattr(_cts,
            'DCfolder', _cts.main_folder.add_folder(NodeId('CTS.DC', 2),
                                                    "DCLED_Control"))
    setattr(_cts,
            'ACfolder', _cts.main_folder.add_folder(NodeId('CTS.AC', 3),
                                                    "ACLED_Control"))
    
    for board in _cts.LED_boards:
        setattr(board, 'node_name', 'CTS.DC.Board%d' % (board.internal_id))
        setattr(board, 'opcua_main_node',
                _cts.DCfolder.add_folder(NodeId(board.node_name, 2),
                                            board.node_name))
        setattr(
            board,
            'opcua_dc_dac', board.opcua_main_node.add_variable(
                NodeId(board.node_name + ".DC_DAC"),
                "DC_DAC",
                0
            )
        )
        setattr(
            board,
            'opcua_dc_dcdc', board.opcua_main_node.add_variable(
                NodeId(board.node_name + ".DC_DCDC"),
                "DC_DCDC",
                0
            )
        )
        setattr(
            board,
            'opcua_ac_dcdc',
            board.opcua_main_node.add_variable(
                NodeId(board.node_name + ".AC_DCDC"),
                "AC_DCDC",
                0
            )
        )
        setattr(
            board,
            'opcua_dc_dcdc_module',
            board.opcua_main_node.add_property(
                NodeId(board.node_name + "._DC_DCDCmodule"),
                "_DC_DCDCmodule",
                board.LEDs[0].can_dcdc_module
            )
        )
        setattr(
            board,
            'opcua_ac_dcdc_module',
            board.opcua_main_node.add_property(
                NodeId(board.node_name + "._AC_DCDCmodule"),
                "_AC_DCDCmodule",
                _cts.LEDs[board.LEDs[0].internal_id - 48 * 11].can_dcdc_module
            )
        )
        setattr(
            board,
            'opcua_dc_dac_module',
            board.opcua_main_node.add_property(
                NodeId(board.node_name + "._DACmodule"),
                "_DACmodule",
                board.LEDs[0].can_dac_module
            )
        )
        setattr(
            board,
            'opcua_dc_dac_channel',
            board.opcua_main_node.add_property(
                NodeId(board.node_name + "._DACchannel"),
                "_DACchannel",
                board.LEDs[0].can_dac_channel
            )
        )
        for led in board.LEDs:
            init_led_node(led, board.opcua_main_node)
    for patch in _cts.LED_patches:
        setattr(patch, 'node_name', 'CTS.AC.Patch%d' % (patch.camera_patch_id))
        setattr(
            patch,
            'opcua_main_node',
            _cts.ACfolder.add_folder(
                NodeId(patch.node_name, 2),
                patch.node_name
            )
        )
        setattr(
            patch,
            'opcua_ac_dac',
            patch.opcua_main_node.add_variable(
                NodeId(patch.node_name + ".AC_DAC"),
                "AC_DAC",
                0
            )
        )
        setattr(
            patch,
            'opcua_ac_dac_module',
            patch.opcua_main_node.add_property(
                NodeId(patch.node_name + "._DACmodule"),
                "_DACmodule",
                patch.LEDs[0].can_dac_module
            )
        )
        setattr(
            patch,
            'opcua_ac_dac_channel',
            patch.opcua_main_node.add_property(
                NodeId(patch.node_name + "._DACchannel"),
                "_DACchannel",
                patch.LEDs[0].can_dac_channel
            )
        )
        for led in patch.LEDs:
            init_led_node(led, patch.opcua_main_node)

    # Now add the functions.
    board = arg_int("Board", "LED Board id")
    patch = arg_int("Patch", "LED Patch id")
    led = arg_int("LED", "LED id")
    led_type = arg_string("LEDType", "LED type (\"AC\" or \"DC\")")
    status = arg_bool("Status", "Status: True(1) or False(0)")
    level = arg_int("DACLevel", "DAC level: int (from 0 to 1023)")
    level_DC = arg_int("DACLevel", "DAC level for DC LEDs: int (from 0 to 1023)")
    level_AC = arg_int("DACLevel", "DAC level for AC LEDs: int (from 0 to 1023)")
    outarg = arg_string("Result", "Result")
    setattr(
        _cts,
        'set_dc_level',
        _cts.main_folder.add_method(
            NodeId('CTS.set_dc_level', 2),
            'set_dc_level',
            setDC_Level,
            [board, level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_ac_level',
        _cts.main_folder.add_method(
            NodeId('CTS.set_ac_level', 2),
            'set_ac_level',
            setAC_Level,
            [patch, level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_led_status',
        _cts.main_folder.add_method(
            NodeId('CTS.set_led_status', 2),
            'set_led_status',
            setLED_Status,
            [led_type, led, status],
            [outarg]
        )
    )
    setattr(
        _cts,
        'all_on',
        _cts.main_folder.add_method(
            NodeId('CTS.all_on', 2),
            'all_on',
            all_on,
            [led_type, level],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_DAC_all_DC',
        _cts.main_folder.add_method(
            NodeId('CTS.set_DAC_all_DC', 2),
            'set_DAC_all_DC',
            set_DAC_all_DC,
            [level_DC],
            [outarg]
        )
    )
    setattr(
        _cts,
        'set_DAC_all',
        _cts.main_folder.add_method(
            NodeId('CTS.set_DAC_all', 2),
            'set_DAC_all',
            set_DAC_all,
            [level_AC, level_DC],
            [outarg]
        )
    )
    #switch_all(on=True)
    setattr(
        _cts,
        'switch_all',
        _cts.main_folder.add_method(
            NodeId('CTS.switch_all', 2),
            'switch_all',
            switch_all,
            [status],
            [outarg]
        )
    )
    setattr(
        _cts,
        'update_LEDparameters',
        _cts.main_folder.add_method(
            NodeId('CTS.update_LEDparameters', 2),
            'update_LEDparameters',
            update_LEDparameters
        )
    )
    setattr(
        _cts,
        'DCDC_ON',
        _cts.main_folder.add_method(
            NodeId('CTS.DCDC_ON', 2),
            'DCDC_ON',
            DCDC_ON
        )
    )
    setattr(
        _cts,
        'DCDC_OFF',
        _cts.main_folder.add_method(
            NodeId('CTS.DCDC_OFF', 2),
            'DCDC_OFF',
            DCDC_OFF
        )
    )


def update_opcua_structure(_cts):
    # First get the LED and DCDC status
    res = com.command(
        _cts.bus,
        range(1, 109),
        'GetLEDandDAC',
        [0x00],
        broadcast=True, broadcastAnswer=True, verbose=False, waitanswer=True
    )
    res = res[0]
    # check the response is the expected code:
    for k in res.keys():
        goodcode = False
        for result in res[k]:
            if result[0] == 0x04:
                goodcode = True
        if not goodcode:
            raise Exception('Answer code not aligned with request...')
    # Get the information for DC leds
    for board in _cts.LED_boards:
        board.opcua_dc_dcdc.set_value(
            res[mod2r(board.opcua_dc_dcdc_module.get_value())][0][4]
        )
        board.opcua_ac_dcdc.set_value(
            res[mod2r(board.opcua_ac_dcdc_module.get_value())][0][4]
        )
        for led in board.LEDs:
            r = mod2r(led.opcua_status_module.get_value())
            status_word = res[r][0][1] << 16 | res[r][0][2] << 8 | res[r][0][3]
            status_mask = 1 << led.opcua_status_channel.get_value()
            led_status = led.opcua_status_channel.get_value()
            led.opcua_status.set_value(
                bool((status_mask & status_word) >> led_status)
            )
    # Get the information for the AC leds
    for patch in _cts.LED_patches:
        for led in patch.LEDs:
            r = mod2r(led.opcua_status_module.get_value())
            status_word = res[r][0][1] << 16 | res[r][0][2] << 8 | res[r][0][3]
            status_mask = 1 << led.opcua_status_channel.get_value()
            led_status = led.opcua_status_channel.get_value()
            led.opcua_status.set_value(
                bool((status_mask & status_word) >> led_status)
            )

    # Then get the DAC status
    res = com.command(_cts.bus, range(1, 109), 'GetLEDandDAC', [0x01],
                      broadcast=True, broadcastAnswer=True,
                      verbose=False, waitanswer=True)
    res = res[0]
    # check the response is the expected code:
    for k in res.keys():
        goodcode = False
        for result in res[k]:
            if result[0] == 0x04:
                goodcode = True
        if not goodcode:
            raise Exception('Answer code not aligned with request...')

    # Get the information for DC leds
    for board in _cts.LED_boards:
        frame = int(board.opcua_dc_dac_channel.get_value() / 3)
        channel = board.opcua_dc_dac_channel.get_value() % 3 * 2 + 1
        r = mod2r(board.opcua_dc_dac_module.get_value())
        board.opcua_dc_dac.set_value(
            res[r][frame][channel] << 8 | res[r][frame][channel + 1] << 8
        )
    # Get the information for AC leds
    for patch in _cts.LED_patches:
        frame = int(patch.opcua_ac_dac_channel.get_value() / 3)
        channel = patch.opcua_ac_dac_channel.get_value() % 3 * 2 + 1
        r = mod2r(patch.opcua_ac_dac_module.get_value())
        patch.opcua_ac_dac.set_value(
            res[r][frame][channel] << 8 | res[r][frame][channel + 1] << 8)


def init_led_node(led, _parent_node):
    '''
    Populating the OPC adress space for LEDs
    '''
    if led.led_type == 'AC':
        setattr(
            led, 'node_name',
            'CTS.AC.Patch%d.LED%d' % (led.camera_patch_id, led.camera_pixel_id)
        )
    else:
        setattr(
            led, 'node_name',
            'CTS.DC.Board%d.LED%d' % (led.led_board, led.camera_pixel_id)
        )
    setattr(
        led,
        'opcua_main_node',
        _parent_node.add_folder(NodeId(led.node_name, 2), led.node_name)
    )
    setattr(
        led, 'opcua_status',
        led.opcua_main_node.add_variable(
            NodeId(led.node_name + ".Status"),
            "Status",
            False
        )
    )
    setattr(
        led,
        'opcua_type',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + ".Type"),
            "Type",
            led.led_type
        )
    )
    setattr(
        led,
        'opcua_pixel_center',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + ".Center"),
            "Center",
            [led.center[0][0], led.center[1][0]]
        )
    )
    setattr(
        led,
        'opcua_dcdc_module',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + "._DCDCmodule"),
            "_DCDCmodule",
            led.can_dcdc_module
        )
    )
    setattr(
        led,
        'opcua_dac_module',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + "._DACmodule"),
            "_DACmodule",
            led.can_dac_module
        )
    )
    setattr(
        led,
        'opcua_dcdc_channel',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + "._DACchannel"),
            "_DACchannel",
            led.can_dac_channel
        )
    )
    setattr(
        led,
        'opcua_status_module',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + "._STATUSmodule"),
            "_STATUSmodule",
            led.can_status_module
        )
    )
    setattr(
        led,
        'opcua_status_channel',
        led.opcua_main_node.add_property(
            NodeId(led.node_name + "._STATUSchannel"),
            "_STATUSchannel",
            led.can_status_channel
        )
    )


ctsserver = None


@uamethod
def setDC_Level(parent, board_number, level):
    ctsserver.cts.LED_boards[board_number].opcua_dc_dac.set_value(level)
    res = None
    level &= 0x3FF
    level_LSB = level & 0xFF
    level_MSB = (level & 0x300) >> 8
    m = ctsserver.cts.LED_boards[board_number].opcua_dc_dac_module.get_value()
    c = ctsserver.cts.LED_boards[board_number].opcua_dc_dac_channel.get_value()
    res = com.command(
        ctsserver.cts.bus,
        [m],
        'SetDACLevel',
        [c, level_MSB, level_LSB],
        waitanswer=False
    )
    return 'done setting DC level=' + str(level) + ' to module ' + str(m) + \
           ' channel ' + str (c) + ', res=' + str(res)


@uamethod
def setAC_Level(parent, patch_number, level):
    res = None
    level &= 0x3FF
    level_LSB = level & 0xFF
    level_MSB = (level & 0x300) >> 8
    patch_internal_number = \
        ctsserver.cts.patch_camera_to_patch_led[patch_number]
    led_patch = ctsserver.cts.LED_patches[patch_internal_number]
    led_patch.opcua_ac_dac.set_value(level)
    m = led_patch.opcua_ac_dac_module.get_value()
    c = led_patch.opcua_ac_dac_channel.get_value()
    res = com.command(
        ctsserver.cts.bus,
        [m],
        'SetDACLevel',
        [c, level_MSB, level_LSB],
        waitanswer=False,
        verbose=False
    )
    return 'done setting lvl=' + str(level) + 'to module ' + str(m) + \
           ' channel ' + str (c) + ', res=' + str(res)


@uamethod
def setLED_Status(parent, led_type, led_number, status):
    res = None
    # Get the LED value, ie, for this given module the value of all the leds
    led_internal_id = ctsserver.cts.pixel_to_led[led_type][led_number]
    mod = ctsserver.cts.LEDs[led_internal_id].opcua_status_module.get_value()
    board = ctsserver.cts.LEDs[led_internal_id].led_board
    led = 0x0
    leds_internal_id = \
        ctsserver.cts.status_modules_to_leds_intenal_id[led_type][mod]
    for l_id in leds_internal_id:
        opcid = ctsserver.cts.LEDs[l_id].camera_pixel_id
        if opcid == led_number:
            ctsserver.cts.LEDs[l_id].opcua_status.set_value(int(status))
        led_status = int(ctsserver.cts.LEDs[l_id].opcua_status.get_value())
        id_in_controler = ctsserver.cts.LEDs[l_id].id_in_led_board % 24
        mask = led_status << id_in_controler
        print('led:', l_id, 'opcua led id:', opcid,
              'id in board:',ctsserver.cts.LEDs[l_id].id_in_led_board,
              'led_status:', led_status, "mask:", mask)
        led |= mask
    print('led:', led)

    dc_dcdc = ctsserver.cts.LED_boards[board].opcua_dc_dcdc.get_value()
    ac_dcdc = ctsserver.cts.LED_boards[board].opcua_ac_dcdc.get_value()
    globalCmd = dc_dcdc if led_type == 'DC' else ac_dcdc
    led_LSB = led & 0xFF
    led_MSB = (led & 0xFF00) >> 8
    led_HSB = (led & 0xFF0000) >> 16

    res = com.command(
        ctsserver.cts.bus,
        [mod],
        'SetLED',
        [led_HSB, led_MSB, led_LSB, globalCmd],
        waitanswer=False
    )
    return 'done setting leds=' + str(led) + 'to module ' + str(mod) + \
           'with DCDC=' + str(globalCmd) + ', res=' + str(res)


@uamethod
def all_on(parent, led_type, level):
    #switch on all led of led_type
    #run again with AC leds after changing DC leds level.
    if led_type == 'DC':
        globalCmd = 1
        channel= 0
    elif led_type == 'AC':
        globalCmd = 0
        channel = 8
    else:
        return 'ERROR, led_type must be "AC" or "DC"'
    res = com.setDACLevel(ctsserver.cts.bus, level, module=None, channel=channel, waitanswer=False)
    res = com.setLED(ctsserver.cts.bus, module=None, globalCmd=globalCmd, waitanswer=False)
    return 'success'


@uamethod
def set_DAC_all_DC(parent, level_DC):
    # DC: channel 0 for half board, other channels invalid
    res = com.setDACLevel(ctsserver.cts.bus, level_DC, module=None, channel=0, waitanswer=False)
    time.sleep(1)


@uamethod
def set_DAC_all(parent, level_AC, level_DC):
    # DC: channel 0 for half board, other channels invalid
    res = com.setDACLevel(ctsserver.cts.bus, level_DC, module=None, channel=0, waitanswer=False)
    time.sleep(.1)
    # AC: channel 8 for half board, other channels to specify a patch
    # as channel 8 invalid for DC leds, their ADC values will not be changed.
    res = com.setDACLevel(ctsserver.cts.bus, level_AC, module=None, channel=8, waitanswer=False)
    time.sleep(.1)


@uamethod
def switch_all(parent, status=True):
    if status:  # on
        led_mask = 0xFFFFFF
    else:  # off
        led_mask = 0x000000
    for module in range(1, 109):
        hw_add =  (module - 1) % 4
        if hw_add == 0:
            # 0 is on for AC
            res = com.setLED(ctsserver.cts.bus, module=module, led_mask = led_mask, globalCmd=0, waitanswer=False)
        elif hw_add == 1:
            # globalCmd = 1 rejected on Hw_add = 1
            res = com.setLED(ctsserver.cts.bus, module=module, led_mask = led_mask, globalCmd=0, waitanswer=False)
        elif hw_add == 2:
            # 1 is on for AC
            res = com.setLED(ctsserver.cts.bus, module=module, led_mask = led_mask, globalCmd=1, waitanswer=False)
        elif hw_add == 3:
            # globalCmd = 1 rejected on Hw_add = 3
            res = com.setLED(ctsserver.cts.bus, module=module, led_mask = led_mask, globalCmd=0, waitanswer=False)
        print(res)
        time.sleep(.1)


@uamethod
def update_LEDparameters(parent):
    com.flushAnswer(ctsserver.cts.bus)
    update_opcua_structure(ctsserver.cts)
    return 'done updating LED parameters'


@uamethod
def DCDC_ON(parent):
    for board in ctsserver.cts.LED_boards:
        print("set DCDC on for board", board.internal_id)
        board.opcua_dc_dcdc.set_value(True)
        board.opcua_ac_dcdc.set_value(False)


@uamethod
def DCDC_OFF(parent):
    for board in ctsserver.cts.LED_boards:
        print("set DCDC off for board", board.internal_id)
        board.opcua_dc_dcdc.set_value(False)
        board.opcua_ac_dcdc.set_value(True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        angle = 0.
    else:
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
