import cts_opcua.cts_opcua_client as cts_client
import cts.cameratestsetup as cameratestsetup
import generator.generator as gen

import matplotlib.pyplot as plt
from ctapipe.io.hessio import hessio_event_source
from ctapipe.io.camera import CameraGeometry
from ctapipe.io.camera import find_neighbor_pixels
from ctapipe import visualization
from utils import mcevent
import logging
from opcua import ua
from astropy import units as u

import numpy as np
import time



class CTSController:
    def __init__(self, logger_name):
        self.log = logging.getLogger(logger_name+'.CTS')
        self.cts = None
        self.cts_client = None
        self.plotting = False
        self.dc_status = None
        self.ac_status = None
        self.dc_level = None
        self.ac_level = None

    def configuration(self,options):
        self.options = options
        # Get the CTS mapping
        try :
            self.cts = cameratestsetup.CTS('config/cts_config_' + str(int(self.options['cts_angle'])) + '.cfg',
                                           'config/camera_config.cfg', angle=float(self.options['cts_angle']), connected=False)
        except Exception as inst:
            raise inst

        # Get the CTS OpcUA client
        try :
            self.cts_client = cts_client.CTSClient()
        except Exception as inst:
            raise inst
        # Prepare plots

        self.plotting = options['plots'] if 'plots' in options.keys() else self.plotting
        if self.plotting:
            self.plots = []
        # Prepare data cube
        self.dc_status = np.ones(1296, dtype=int) * 0
        self.ac_status = np.ones(1296, dtype=int) * 0
        self.dc_level = np.ones(1296, dtype=int) * 0
        self.ac_level = np.ones(1296, dtype=int) * 0
        if self.plotting:
            self.initialise_plots()
        # Make the plots interactive
        # plt.ion()
        if self.plotting:
            self.plot()
        print('exit config of the CTSControloer')

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('---|> The client will be reset and turned off, wait...')
        self.reset_cts()

    def initialise_plots(self):
        # first load in a very nasty way the camera geometry
        filename = '/data/software/CTS/config/randomMC.simtel.gz'
        # test
        pix_x,pix_y,pix_id=[],[],[]
        pixels = self.cts.camera.Pixels
        pixelspresent = list(self.cts.pixel_to_led['DC'].keys())
        for pix in pixels:
            if pix.ID in pixelspresent:
                pix_x.append(pix.center[0])
                pix_y.append(pix.center[1])
                pix_id.append(pix.ID)
            else:
                pix_x.append(-200.)
                pix_y.append(-200.)
                pix_id.append(pix.ID)

        pix_x = list(pix_x)
        pix_y = list(pix_y)
        pix_id = list(pix_id)
        neighbors_pix = find_neighbor_pixels(pix_x, pix_y,30.)
        geom = CameraGeometry(0,pix_id, pix_x*u.mm, pix_y*u.mm,np.ones((1296))*400.,neighbors_pix,'hexagonal')
        plt.figure(0,figsize=(20,6))
        self.plots = []
        plt.subplot(1, 2, 1)
        self.plots.append(visualization.CameraDisplay(geom, title='AC status', norm='lin', cmap='coolwarm'))
        self.plots[-1].add_colorbar()
        self.plots[-1].image = np.multiply(self.ac_status, self.ac_level)
        plt.subplot(1, 2, 2)
        self.plots.append(visualization.CameraDisplay(geom, title='DC status', norm='lin', cmap='coolwarm'))
        self.plots[-1].add_colorbar()
        self.plots[-1].image = np.multiply(self.dc_status, self.dc_level)

    # Helper functions
    def update(self):
        self.cts_client.update()

    def reset_cts(self):
        """
        reset()

        A function to put back all led to 0

        """
        plotting = True if self.plotting else False
        self.plotting = False
        for led_type in ['AC', 'DC']:
            for pixel in self.cts.pixel_to_led[led_type].keys():
                self.turn_off(pixel, led_type)
        self.plotting = True if plotting else False
        self.log.info('Rest of the CTS has been performed')

    def turn_on(self, pixel, led_type, level, enable_plot = True):
        """
        turn_on(pixel,led_type,level)

        A function to turn on the AC or DC led in front of a given pixel with a given level

        Input :
               - pixel : the software pixel id in front of which the led should be turned on (int)
               - led_type : the type of led (str could be 'AC' or 'DC')
               - level : the DAC level
        """
        if led_type == 'AC':
            patch = self.cts.LEDs[self.cts.pixel_to_led['AC'][pixel]].camera_patch_id
            self.cts_client.set_ac_level(patch, level)
            self.cts_client.set_led_status('AC', pixel, True)
            self.ac_level[pixel] = level
            self.ac_status[pixel] = 1
            if self.plotting and enable_plot:
                self.plot()
        if led_type == 'DC':
            board = self.cts.LEDs[self.cts.pixel_to_led['DC'][pixel]].led_board
            self.cts_client.set_dc_level(board, level)
            self.cts_client.set_led_status('DC', pixel, True)
            self.dc_level[pixel] = level
            self.dc_status[pixel] = 1
            if self.plotting and enable_plot:
                self.plot()

    def turn_off(self, pixel, led_type, enable_plot = True):
        """
        turn_off(pixel,led_type)

        A function to turn off the AC or DC led in front of a given pixel

        Input :
               - pixel : the software pixel id in front of which the led should be turned on (int)
               - led_type : the type of led (str could be 'AC' or 'DC')
        """
        if led_type == 'AC':
            patch = self.cts.LEDs[self.cts.pixel_to_led['AC'][pixel]].camera_patch_id
            self.cts_client.set_ac_level(patch, 0)
            self.cts_client.set_led_status('AC', pixel, False)
            self.dc_level[pixel] = 0
            self.dc_status[pixel] = 0
            if self.plotting and enable_plot:
                self.plot()
        if led_type == 'DC':
            board = self.cts.LEDs[self.cts.pixel_to_led['DC'][pixel]].led_board
            self.cts_client.set_dc_level(board, 0)
            self.cts_client.set_led_status('DC', pixel, False)
            self.dc_level[pixel] = 0
            self.dc_status[pixel] = 0
            if self.plotting and enable_plot:
                self.plot()

    def all_on(self, led_type, level ):
        """
        all_on(led_type,level)

        A function to turn on all CTS led AC or DC

        Input:
              - led_type : type of the leds to be turned on 'AC' or 'DC' (str)
              - level    : the DAC level (int)

        """
        for pixel in self.cts.pixel_to_led[led_type].keys():
            self.turn_on(pixel, led_type, level, enable_plot = False)

    def all_off(self, led_type):
        """
        all_on(led_type,level)

        A function to turn on all CTS led AC or DC

        Input:
              - led_type : type of the leds to be turned on 'AC' or 'DC' (str)
              - level    : the DAC level (int)

        """
        for pixel in self.cts.pixel_to_led[led_type].keys():
            self.turn_off(pixel, led_type, enable_plot = False)


    def print_status(self):
        """
        print_status()

        A function to visualise in command line the status of each LED

        It will print the values stored in the datapoints published by the server and should be
        representative of the values in hardware

        To force a reading of the values in the hardware first call update() which will update
        the datapoints with results of can request

        """
        pixel_list = list(self.cts.pixel_to_led['DC'].keys())
        pixel_list.sort()
        self.log.info('============================================== Status')
        for pix in pixel_list:
            board = self.cts.LEDs[self.cts.pixel_to_led['DC'][pix]].led_board
            patch = self.cts.LEDs[self.cts.pixel_to_led['AC'][pix]].camera_patch_id
            nameb = 'CTS.DC.Board' + str(board)
            namep = 'CTS.AC.Patch' + str(patch)
            self.log.info('| pix patch ledboard:', "%04d" % pix, "%03d" % patch, "%02d" % board, end=' ')
            self.dc_level[pix] = self.cts_client.client.get_node(ua.NodeId(nameb + '.DC_DAC')).get_value()
            self.log.info('| DC_Level:', self.dc_level[pix], end=' ')
            self.ac_level[pix] = self.cts_client.client.get_node(ua.NodeId(namep + '.AC_DAC')).get_value()
            self.log.info('| AC_Level:', self.ac_level[pix], end=' ')
            self.log.info('| DC DCDC:', self.cts_client.client.get_node(ua.NodeId(nameb + '.DC_DCDC')).get_value(), end=' ')
            self.log.info('| AC DCDC:', 0 if self.cts_client.client.get_node(
                ua.NodeId(nameb + '.AC_DCDC')).get_value() > 0.5 else 1, end=' ')  # opposite...
            self.ac_status = int(
                self.cts_client.client.get_node(ua.NodeId(namep + '.LED' + str(pix) + '.Status')).get_value())
            self.log.info('| AC Status:', self.ac_status[pix], end=' ')
            self.dc_status[pix] = int(
                self.cts_client.client.get_node(ua.NodeId(nameb + '.LED' + str(pix) + '.Status')).get_value())
            self.log.info('| DC Status:', self.dc_status[pix])
        if self.plotting:
            self.plot()

    def write_event(self, patch_level, pix_status, level_dc):
        """
        write_event(patch_level,pix_status,level_dc)

        Write an event in the CTS out of a list of patches level, lighten pixels and NSB level

        Input :
               - patch_level : dictionnary conatining for each patch id (key) the DAC level to apply (value)
               - pix_status  : dictionnary containing for each pixel id (key) its status (True/False for ON/OFF)
               - level_dc    : DAC of the DC leds to emulate the NSB
        """
        # DC Logic: apply DC level to all board
        for board in self.cts.LED_boards:
            self.cts_client.set_dc_level(board.internal_id, int(round(level_dc)))
        # DC Logic: turn on all LED
        for pix_DC in self.cts.pixel_to_led['DC'].keys():
            self.cts_client.set_led_status('DC', pix_DC, True)

        # AC Logic: apply AC level to all patch
        for patch in patch_level.keys():
            self.cts_client.set_ac_level(patch, int(round(patch_level[patch])))

        # AC Logic: turn on all LED
        for pix_AC in self.cts.pixel_to_led['AC'].keys():
            self.cts_client.set_led_status('AC', pix_AC, pix_status[pix_AC])

        if self.plotting: 
            self.plot()

    def write_mc_event(self, nsb_level=500, evtnum=0,
                       filename='/home/sterody/Documents/CTS/OpcUaCameraTestSetup/data/gamma_0.csv'):
        """
        write_event(nsb_level,evtnum,filename)

        Write an event in the CTS from MC event input

        Input :
               - nsb_level    : DAC of the DC leds to emulate the NSB
               - evtnum       : event number in the file
               - filename     : input file path
        """
        # Load the event from the file
        pixel_mc = mcevent.load_event(evtnum, filename)
        # Get the patch levels and pixel status
        camera_patches_mean, pixel_status = mcevent.compute_led_patches_mean(self.cts, pixel_mc)
        # Write the event in the CTS
        self.write_event(camera_patches_mean, pixel_status, nsb_level)


    def plot(self):
        self.plots[0].image = np.multiply(self.ac_status, self.ac_level)
        self.plots[1].image = np.multiply(self.dc_status, self.dc_level)
        plt.show()
