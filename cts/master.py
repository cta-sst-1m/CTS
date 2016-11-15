import cts_opcua.cts_opcua_client as cts_client
import cts.cameratestsetup as cameratestsetup
import generator.generator as gen

import matplotlib.pyplot as plt
from ctapipe.io.hessio import hessio_event_source
from ctapipe.io.camera import CameraGeometry
from ctapipe import visualization
from utils import mcevent

from opcua import ua

import numpy as np
import time


class CTSMaster:
    def __init__(self, angle_cts, plotting=True):
        # Get the CTS mapping
        self.cts = cameratestsetup.CTS('config/cts_config_' + str(int(angle_cts)) + '.cfg',
                                       'config/camera_config.cfg', angle=angle_cts, connected=False)
        # Get the CTS OpcUA client
        self.cts_client = cts_client.CTSClient()
        # Get the generator for triggering AC leds and digicam
        self.generator = gen.Generator(url="129.194.55.68")
        self.generator.load_configuration(conf_type='continuous')
        # Get the digicam OpcUA client
        self.digicam_client = None
        # Prepare plots
        self.plotting = plotting
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

    def __del__(self):
        print('---|> The client will be reset and turned off, wait...')
        self.reset()

    def initialise_plots(self):
        # first load in a very nasty way the camera geometry
        filename = "/data/datasets/gamma_20deg_180deg_run100___cta-prod3-merged_desert-2150m--subarray-2-nosct.simtel.gz"

        # get the geometry
        geom = None

        for event in hessio_event_source(filename):
            for telid in event.dl0.tels_with_data:
                if event.dl0.tel[telid].num_pixels != 1296: continue
                print("Telescope ID = ", telid)
                geom = CameraGeometry.guess(*event.meta.pixel_pos[telid],
                                            event.meta.optical_foclen[telid])
                if geom.cam_id != 'SST-1m': break
            if geom != None: break

        # get the geometry
        geom = None
        for event in hessio_event_source(filename):
            for telid in event.dl0.tels_with_data:
                if event.dl0.tel[telid].num_pixels != 1296: 
                    continue
                print("Telescope ID = ", telid)
                geom = CameraGeometry.guess(*event.meta.pixel_pos[telid],
                                            event.meta.optical_foclen[telid])
                if geom.cam_id != 'SST-1m':
                    break
            if geom is not None:
                break

        plt.figure(0)
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

    def reset(self):
        """
        reset()

        A function to put back all led to 0

        """
        for led_type in ['AC', 'DC']:
            for pixel in self.cts.pixel_to_led[led_type].keys():
                self.turn_off(pixel, led_type)

    def loop_over_dc_pixels(self, level, timeout=0.1):
        """
        loop_over_dc_pixels(level,timeout)

        A function to light DC pixels one after the other in increasing software pixel id

        Inputs :
                 - level   : the DAC level to apply (int)
                 - timeout : the amount of time, in s, to keep the pixels on (float)
        """
        # loop over the boards and apply the DAC level
        for board in self.cts.LED_boards:
            self.cts_client.set_dc_level(board.internal_id, level)
        # loop over the pixels
        pixel_list = list(self.cts.pixel_to_led['DC'].keys())
        pixel_list.sort()
        for i, pix in enumerate(pixel_list):
            self.dc_level[pix] = 0
            if i > 0:
                # turn off the previous pixel
                self.cts_client.set_led_status('DC', pixel_list[i - 1], False)
                self.dc_status[pix] = 0
            # turn on this pixel
            self.cts_client.set_led_status('DC', pixel_list[i], True)
            self.dc_status[pix] = 1
            if self.plotting:
                self.plot()
            time.sleep(timeout)
        # turn off the last pixel
        self.cts_client.set_led_status('DC', pixel_list[-1], False)
        self.dc_status[pixel_list[-1]] = 0
        # put back all DAC level to 0
        for board in self.cts.LED_boards:
            self.cts_client.set_dc_level(board.internal_id, 0)

    def loop_over_ac_pixels(self, level, timeout=0.05, n_triggers=10):
        """
        loop_over_ac_pixels(level,timeout,trigger,n_trigger)

        A function to light AC pixels one after the other in increasing software pixel id

        Inputs :
                 - level   : the DAC level to apply (int)
                 - timeout : the amount of time, in s, to keep the pixels on (float)
                 - n_trigger : number of consecutive trigger for AC
        """
        # Initialise the trigger
        #self.generator.load_configuration(conf_type='burst')
        #self.generator.configure_trigger(n_trigger=n_triggers)
        # loop over the patches to set the DAC level
        for patch in self.cts.LED_patches:
            self.cts_client.set_ac_level(patch.camera_patch_id, level)
        # loop over the pixels
        pixel_list = list(self.cts.pixel_to_led['AC'].keys())
        pixel_list.sort()
        for i, pix in enumerate(pixel_list):
            if i > 0:
                # turn off the previous pixel
                self.cts_client.set_led_status('AC', pixel_list[i - 1], False)
            time.sleep(timeout)
            # turn on this pixel
            self.cts_client.set_led_status('AC', pixel_list[i], True)
            self.generator.start_trigger()
            time.sleep(timeout)
        # turn off the last pixel
        self.cts_client.set_led_status('AC', pixel_list[-1], False)
        # loop over hte patches and put the DAC back to 0
        for patch in self.cts.LED_patches:
            self.cts_client.set_ac_level(patch.camera_patch_id, 0)
        # put back the default trigger configruation
        #self.generator.load_configuration(conf_type='continuous')

    def loop_over_dc_patches(self, level, timeout=0.5):
        """
        loop_over_dc_patches(level,timeout)

        A function to light DC patches one after the other in increasing software patch id

        Inputs :
                 - level   : the DAC level to apply (int)
                 - timeout : the amount of time, in s, to keep the patches on (float)
        """

        # set the level on all LED boards
        for board in self.cts.LED_boards:
            self.cts_client.set_dc_level(board.internal_id, level)
        # loop over the patches

        patch_list = list(self.cts.patch_camera_to_patch_led.keys())
        patch_list.sort()

        for i, patch in enumerate(patch_list):
            ledpatch = self.cts.LED_patches[self.cts.patch_camera_to_patch_led[patch]]
            if i > 0:
                # turn off the previous patch
                ledpatch_prev = self.cts.LED_patches[
                    self.cts.patch_camera_to_patch_led[self.cts.patch_camera_to_patch_led.keys()[i - 1]]]
                for pix in ledpatch_prev.leds_camera_pixel_id:
                    self.cts_client.set_led_status('DC', pix, False)
            # turn on the present patch
            for pix in ledpatch.leds_camera_pixel_id:
                self.cts_client.set_led_status('DC', pix, True)
            time.sleep(timeout)

        # turn off last patch
        for pix in self.cts.LED_patches[self.cts.patch_camera_to_patch_led[patch_list[-1]]].leds_camera_pixel_id:
            self.cts_client.set_led_status('DC', pix, False)
        # set back the level to 0
        for board in self.cts.LED_boards:
            self.cts_client.set_dc_level(board.internal_id, 0)

    def loop_over_ac_patches(self, level, timeout=0.5, n_triggers=10):
        """
        loop_over_ac_patches(level,timeout)

        A function to light AC patches one after the other in increasing software patch id

        Inputs :
                 - level   : the DAC level to apply (int)
                 - timeout : the amount of time, in s, to keep the patches on (float)
                 - n_triggers: number of consecutive triggers
        """
        # configure the trigger
        #self.generator.load_configuration(conf_type='burst')
        #self.generator.configure_trigger(n_trigger=n_triggers)

        # loop over the patches
        patch_list = list(self.cts.patch_camera_to_patch_led.keys())
        patch_list.sort()

        for i, patch in enumerate(patch_list):
            ledpatch = self.cts.LED_patches[self.cts.patch_camera_to_patch_led[patch]]
            if i > 0:
                # turn off the previous patch
                ledpatch_prev = self.cts.LED_patches[
                    self.cts.patch_camera_to_patch_led[self.cts.patch_camera_to_patch_led.keys()[i - 1]]]
                for pix in ledpatch_prev.leds_camera_pixel_id:
                    self.cts_client.set_led_status('AC', pix, False)
                # put back the DAC level to 0
                self.cts_client.set_ac_level(patch, 0)
            # turn on the present patch
            for pix in ledpatch.leds_camera_pixel_id:
                self.cts_client.set_led_status('AC', pix, True)
            # turn on the DAC level
            self.cts_client.set_ac_level(patch, level)
            self.generator.start_trigger()
            time.sleep(timeout)

        # turn off last patch
        for pix in self.cts.LED_patches[self.cts.patch_camera_to_patch_led[patch_list[-1]]].leds_camera_pixel_id:
            self.cts_client.set_led_status('AC', pix, False)
        # set back the level to 0
        for patch in self.cts.LED_patches:
            self.cts_client.set_ac_level(patch.camera_patch_id, 0)

        # put back the default trigger configruation
        #self.generator.load_configuration(conf_type='continuous')

    def turn_on(self, pixel, led_type, level):
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
            self.generator.start_trigger()
        if led_type == 'DC':
            board = self.cts.LEDs[self.cts.pixel_to_led['DC'][pixel]].led_board
            self.cts_client.set_dc_level(board, level)
            self.cts_client.set_led_status('DC', pixel, True)
            self.dc_level[pixel] = level
            self.dc_status[pixel] = 1

    def turn_off(self, pixel, led_type):
        """
        turn_off(pixel,led_type)

        A function to turn off the AC or DC led in front of a given pixel

        Input :
               - pixel : the software pixel id in front of which the led should be turned on (int)
               - led_type : the type of led (str could be 'AC' or 'DC')
        """
        if led_type == 'AC':
            self.generator.stop_trigger()
            patch = self.cts.LEDs[self.cts.pixel_to_led['AC'][pixel]].camera_patch_id
            self.cts_client.set_ac_level(patch, 0)
            self.cts_client.set_led_status('AC', pixel, False)
            self.dc_level[pixel] = 0
            self.dc_status[pixel] = 0
        if led_type == 'DC':
            board = self.cts.LEDs[self.cts.pixel_to_led['DC'][pixel]].led_board
            self.cts_client.set_dc_level(board, 0)
            self.cts_client.set_led_status('DC', pixel, False)
            self.dc_level[pixel] = 0
            self.dc_status[pixel] = 0

    def all_on(self, led_type, level):
        """
        all_on(led_type,level)

        A function to turn on all CTS led AC or DC

        Input:
              - led_type : type of the leds to be turned on 'AC' or 'DC' (str)
              - level    : the DAC level (int)

        """
        for pixel in self.cts.pixel_to_led[led_type].keys():
            self.turn_on(pixel, led_type, level)
        self.generator.start_trigger()

    def all_off(self, led_type):
        """
        all_on(led_type,level)

        A function to turn on all CTS led AC or DC

        Input:
              - led_type : type of the leds to be turned on 'AC' or 'DC' (str)
              - level    : the DAC level (int)

        """
        self.generator.stop_trigger()
        for pixel in self.cts.pixel_to_led[led_type].keys():
            self.turn_off(pixel, led_type)

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
        print('============================================== Status')
        for pix in pixel_list:
            board = self.cts.LEDs[self.cts.pixel_to_led['DC'][pix]].led_board
            patch = self.cts.LEDs[self.cts.pixel_to_led['AC'][pix]].camera_patch_id
            nameb = 'CTS.DC.Board' + str(board)
            namep = 'CTS.AC.Patch' + str(patch)
            print('| pix patch ledboard:', "%04d" % pix, "%03d" % patch, "%02d" % board, end=' ')
            self.dc_level[pix] = self.cts_client.client.get_node(ua.NodeId(nameb + '.DC_DAC')).get_value()
            print('| DC_Level:', self.dc_level[pix], end=' ')
            self.ac_level[pix] = self.cts_client.client.get_node(ua.NodeId(namep + '.AC_DAC')).get_value()
            print('| AC_Level:', self.ac_level[pix], end=' ')
            print('| DC DCDC:', self.cts_client.client.get_node(ua.NodeId(nameb + '.DC_DCDC')).get_value(), end=' ')
            print('| AC DCDC:', 0 if self.cts_client.client.get_node(
                ua.NodeId(nameb + '.AC_DCDC')).get_value() > 0.5 else 1, end=' ')  # opposite...
            self.ac_status = int(
                self.cts_client.client.get_node(ua.NodeId(namep + '.LED' + str(pix) + '.Status')).get_value())
            print('| AC Status:', self.ac_status[pix], end=' ')
            self.dc_status[pix] = int(
                self.cts_client.client.get_node(ua.NodeId(nameb + '.LED' + str(pix) + '.Status')).get_value())
            print('| DC Status:', self.dc_status[pix])
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

    def loop_mc_event(self, nevent, nsb_level=500,
                      filename='/home/sterody/Documents/CTS/OpcUaCameraTestSetup/data/gamma_0.csv', n_triggers=1000):

        self.generator.load_configuration(conf_type='burst')
        self.generator.configure_trigger(n_trigger=n_triggers)
        for i in range(nevent):
            self.write_mc_event(nsb_level, i, filename)
            # TODO Start run
            self.generator.start_trigger()
            # TODO Stop run (or give different runID

        # put back the default trigger configruation
        self.generator.load_configuration(conf_type='continuous')

    def plot(self):
        self.plots[0].image = np.multiply(self.ac_status, self.ac_level)
        self.plots[1].image = np.multiply(self.dc_status, self.dc_level)
        plt.show()
