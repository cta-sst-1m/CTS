import numpy as np
import sys

if sys.version_info[0] == 3:
    import cts_core.geometry as gp
    import cts_core.camera as camera
else:
    import geometry as gp
    import camera as camera

"""
Define the structure of CTS

"""


class LED():
    def __init__(
            self,
            _id,
            _x,
            _y,
            _led_type,
            _led_board,
            _led_patch,
            _id_in_led_board,
            _id_in_led_patch,
            _camera_pixel_id,
            _camera_patch_id,
            _cts_angle):
        """
        Base class for LED representation

        """

        # Define various indices
        self.internal_id = _id
        # OLD:(_led_board * 16 + _led_patch) * 3 + \
        # OLD:               _id_in_led_patch + (0 if _led_type == 'AC' else 48 * 11)
        self.led_type = _led_type
        self.led_board = _led_board
        self.led_patch = _led_patch  # OLD:(_led_board * 16 + _led_patch)
        self.id_in_led_board = _id_in_led_board
        self.id_in_led_patch = _id_in_led_patch
        self.camera_pixel_id = _camera_pixel_id
        self.camera_patch_id = _camera_patch_id
        self.angle_configuration = _cts_angle

        # Define geometry setup_components
        # if _has_geometry:
        self._init_geometry(_x, _y)

        # Define CAN related variables
        self._init_can_adressing()

    def _init_geometry(self, _x, _y):
        """
        Initialize the geometry of the led element (graph, vertices)

        """
        # rotation to apply to the leds
        _rotation = 0. if self.led_board == 1 else (
            240. if self.led_board == 2 else 140.)
        # shift due to misalignement of the central led boards
        if self.led_board == 2:
            _x += 1.5 * 24.3
            _y -= 0.8 * 24.3
        elif self.led_board == 3:
            _y -= 1.7 * 24.3

        self.vertices = gp.createPixel(_x, _y, d=24.3, rotation=_rotation)
        # Apply rotation matrix to the vertices
        theta = np.radians(self.angle_configuration)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array([[c, -s], [s, c]])
        _tmpvert = R.dot(
            np.array([list(self.vertices[0]), list(self.vertices[1])]))
        self.vertices = _tmpvert[0], _tmpvert[1]

        # Rotate the pixel center
        _tmpcenter = R.dot(np.array([[_x], [_y]]))
        self.center = (_tmpcenter[0], _tmpcenter[1])

    def _init_can_adressing(self):
        '''
        Definition of the CAN module and channels to be adressed to set the LED status, DAC level and DCDC
        '''
        self.can_dcdc_module = self.led_board * 4 + \
                               1 if self.led_type == 'AC' else self.led_board * 4 + 3

        self.can_dac_module = self.led_board * 4 + 1 + \
                              int(self.id_in_led_board / 24) if self.led_type == 'AC' else self.led_board * 4 + 3

        self.can_dac_channel = (
            self.led_patch %
            8) if self.led_type == 'AC' else 0

        self.can_status_module = self.led_board * 4 + 1 + \
                                 int(
                                     self.id_in_led_board / 24) if self.led_type == 'AC' else self.led_board * 4 + 3 + int(
            self.id_in_led_board / 24)
        self.can_status_channel = self.id_in_led_board % 24


class LEDPatch():
    """
    Base class for LED Patch representation (holds AC LEDs)

    """

    def __init__(self, _id, _leds, _has_geometry=True):
        self.internal_id = _id
        self.leds_internal_id = []
        self.leds_id_in_led_board = []
        self.leds_camera_pixel_id = []
        self.camera_patch_id = -1
        # Append the LEDs
        self.LEDs = _leds
        # Propagate some info contained in the LEDs
        for l in self.LEDs:
            self.leds_id_in_led_board.append(l.id_in_led_board)
            self.leds_internal_id.append(l.internal_id)
        self.id_in_led_board = self.LEDs[0].led_patch
        self.led_board = self.LEDs[0].led_board

        # Define geometry setup_components
        if _has_geometry:
            self._init_geometry()

    def _init_geometry(self):
        '''
        Initialize the geometry of the led element (graph, vertices)

        '''
        self.vertices = gp.createPatch([l.vertices for l in self.LEDs])

    def initialise_camera_links(self):
        for l in self.LEDs:
            self.leds_camera_pixel_id.append(l.camera_pixel_id)


class LEDBoard():
    """
    Base class for LED board representation (holds DC LEDs)

    """

    def __init__(self, _id, _leds):
        self.internal_id = _id
        self.leds_internal_id = []
        self.leds_camera_pixel_id = []
        self.patches_internal_id = []
        self.patches_camera_patch_id = []
        # Append the DC LEDs
        self.LEDs = _leds
        # Propagate some info contained in the LEDs
        for l in self.LEDs:
            self.leds_internal_id.append(l.internal_id)
            self.patches_internal_id.append(l.led_patch)
            self.patches_internal_id = list(set(self.patches_internal_id))

    def initialise_camera_links(self):
        for l in self.LEDs:
            self.leds_camera_pixel_id.append(l.camera_pixel_id)
            self.patches_camera_patch_id.append(l.camera_patch_id)
            self.patches_camera_patch_id = list(
                set(self.patches_camera_patch_id))


class CTS():
    """
    Main Class for the camera test setup representation

    Holds the Camera and the LEDs
    """

    def __init__(
            self,
            cts_config_file,
            camera_config_file,
            angle,
            connected=True):

        _map_dict = self._build_cts_mapping(cts_config_file)

        # Create the pixelList
        self.LEDs = [
            LED(
                p,
                _map_dict['x[mm]'][i],
                _map_dict['y[mm]'][i],
                _map_dict['led_type'][i],
                _map_dict['led_board'][i],
                _map_dict['led_patch'][i],
                _map_dict['led_id_in_board'][i],
                _map_dict['led_id_in_patch'][i],
                _map_dict['pixel_sw'][i],
                _map_dict['patch_sw'][i],
                angle
            )
            for i, p in enumerate(
                _map_dict['led_number'])]

        # Store the list of leds
        _patches = [[None] * 3 for i in range(max(_map_dict['led_patch']) + 1)]
        _boards = [[None] * 48 for i in range(max(_map_dict['led_board']) + 1)]

        for i, led in enumerate(self.LEDs):
            if led.led_type == 'AC':
                _patches[led.led_patch][led.id_in_led_patch] = self.LEDs[i]
            if led.led_type == 'DC':
                _boards[led.led_board][led.id_in_led_board] = self.LEDs[i]
        # Create patches List
        self.LED_patches = [LEDPatch(i, _leds)
                            for i, _leds in enumerate(_patches)]
        # Create board List
        self.LED_boards = [LEDBoard(i, _leds)
                           for i, _leds in enumerate(_boards)]

        # Map the CTS representation to the camera representation
        self.camera = camera.Camera(camera_config_file)

        self._match_camera_to_cts()
        # Some usefull map
        self._map_status_modules_to_led()

        for patch in self.LED_patches:
            patch.initialise_camera_links()
        for board in self.LED_boards:
            board.initialise_camera_links()
        #
        self.connected = connected

        #

        self.plots = {}

    '''
    Initialisation functions
    '''

    def _build_cts_mapping(self, _config_file):
        # Get the configuration from file
        f = open(_config_file, 'r')
        keys = []
        line = ''
        while '# HEADER' not in line:
            line = f.readline()
        keys = f.readline().split('# ')[1].split('\n')[0].split('\t')
        line = f.readline()
        lines = list(
            map(list, zip(*[l.split('\n')[0].split('\t') for l in f.readlines()])))
        _map_dict = dict(zip(keys, lines))
        for k in _map_dict.keys():
            if k.count('[mm]') > 0:
                _map_dict[k] = [float(x) for x in _map_dict[k]]
            elif k.count('led_type') > 0:
                _map_dict[k] = [str(x) for x in _map_dict[k]]
            else:
                _map_dict[k] = [int(x) for x in _map_dict[k]]

        # Sort by LED
        for k in filter(lambda x: x != 'led_number', _map_dict.keys()):
            _map_dict[k] = [v[1] for v in sorted(zip(_map_dict['led_number'], _map_dict[k]))]
        _map_dict['led_number'].sort()
        return _map_dict

    def _match_camera_to_cts(self):
        self.pixel_to_led = {'AC': {}, 'DC': {}}
        self.patch_camera_to_patch_led = {}
        for i, l in enumerate(self.LEDs):
            self.pixel_to_led[l.led_type][l.camera_pixel_id] = l.internal_id
        for p in self.LED_patches:
            p.camera_patch_id = p.LEDs[0].camera_patch_id
            self.patch_camera_to_patch_led[p.camera_patch_id] = p.LEDs[0].led_patch

    def _map_status_modules_to_led(self):
        self.status_modules_to_leds_intenal_id = {'AC': {}, 'DC': {}}
        for i, l in enumerate(self.LEDs):
            if l.can_status_module in self.status_modules_to_leds_intenal_id[
                l.led_type]:
                self.status_modules_to_leds_intenal_id[l.led_type][
                    l.can_status_module].append(l.internal_id)
            else:
                self.status_modules_to_leds_intenal_id[
                    l.led_type][
                    l.can_status_module] = [
                    l.internal_id]


if __name__ == '__main__':
    c = CTS('../config/cts_config_0.cfg', '../config/camera_config.cfg', angle=0., connected=False)
    pix_list = c.pixel_to_led['AC'].keys()
    pix_list.sort()
