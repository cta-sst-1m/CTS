import cts_opcua.cts_opcua_client as cts_client
import cts.cameratestsetup as cameratestsetup
import generator.generator as gen

import matplotlib.pyplot as plt
from ctapipe.io.hessio import hessio_event_source
from ctapipe.io.camera import CameraGeometry
from ctapipe.io.camera import find_neighbor_pixels
from ctapipe import visualization
from utils import mcevent

from opcua import ua
from astropy import units as u

import numpy as np
import time


class MTSMaster:
    def __init__(self ):
        #self.generatorMaster = gen.Generator(url="129.194.52.244")
        #self.generatorMaster.apply_config('burst')
        self.generatorSlave = gen.Generator(url="129.194.53.100")
        self.generatorSlave.apply_config('burst')
        self.generatorSlave.inst.write('OUTPUT NORMAL')
        # Get the digicam OpcUA client

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('---|> The client will be reset and turned off, wait...')
        self.reset()


    def dark_run(genM, genS):
        """
        Setup the trigger configruation, data taking configuration, and control the led for dark_run
        :param genS:
        :return:
        """
        return

    def low_light(genM, genS):
        """
        Setup the trigger configruation, data taking configuration, and control the led for dark_run
        :param genS:
        :return:
        """
        return

    def medium_light(genM, genS):
        """
        Setup the trigger configruation, data taking configuration, and control the led for dark_run
        :param genS:
        :return:
        """
        return

    def high_light(genM, genS):
        """
        Setup the trigger configruation, data taking configuration, and control the led for dark_run
        :param genS:
        :return:
        """
        return

    def turn_on(self, level):
        """
        A function to turn on the AC or DC led with a given level
        """
        offset = level / 2
        self.generatorSlave.inst.write('AMPL %f'%level)
        self.generatorSlave.inst.write('DCOFFS -{0:.2f}'.format(offset))
        return

    def turn_off(self, led_type):
        """
        A function to turn on the AC or DC led with a given level
        """
        self.generatorSlave.inst.write('AMPL 0.')
        return



    def dry_runs(self,n_batch=20,batch_size=1000,freq_pulse=300,timeout=60):
        # first make sure the leds are at 0
        self.reset()
        # then configrue the trigger
        self.generatorMaster.configure_trigger(n_pulse = batch_size,freq=freq_pulse)
        i=0
        while i < n_batch:
            self.generatorMaster.start_trigger_sequence()
            time.sleep(timeout)



if __name__ == "__main__":
    mtsmaster = MTSMaster()