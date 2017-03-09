import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger

protocol_name = 'AC_LED_SCAN'

def prepare_run(master_fsm):
    '''

    :param master_fsm:
    :return:
    '''

    log = logging.getLogger(sys.modules['__main__'].__name__)

    log.info('\033[1m\033[91m\t\t-|> Start the AC LED SCAN Protocol\033[0m')

    if not allocate(master_fsm): return False
    if not configure(master_fsm): return False
    if not start_run(master_fsm): return False

    return True


def run_level(master_fsm,timeout):

    if not start_trigger(master_fsm): return False
    time.sleep(timeout)
    if not stop_trigger(master_fsm): return False

    return True



def end_run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    if not stop_run(master_fsm): return False
    if not reset(master_fsm): return False
    if not deallocate(master_fsm): return False

    # ALLOCATE
    log.info('\033[1m\033[91m\t\t-|> End the AC LED SCAN Protocol\033[0m')
    return True



def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    # Some preliminary configurations
    master_fsm.options['generator_configuration']['number_of_pulses'] =  \
        master_fsm.options['protocol_configuration']['events_per_level']

    master_fsm.options['writer_configuration']['max_evts_per_file'] = \
        master_fsm.options['protocol_configuration']['events_per_level']*5

    # Call the FSMs transition to start the run
    if not prepare_run(master_fsm):
        log.error('Failed to prepare the AC LED SCAN run')
        return False

    # Turn on the AC LEDs
    master_fsm.elements['cts_core'].all_on('AC',0)
    # Get the AC LEDs level to run
    AC_DAC_Levels = master_fsm.options['protocol_configuration']['levels']

    # Define the progress bar
    log.info('\033[1m\033[91m\t\t-|> Start the AC DAC level loop\033[0m' )
    pbar = tqdm(total=len(AC_DAC_Levels))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    for i,level in enumerate(AC_DAC_Levels) :
        for patch in master_fsm.elements['cts_core'].cts.LED_patches:
            master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, level)

        log.debug('\033[1m\033[91m\t\t-|> Level%d\033[0m' % level)
        timeout = float(master_fsm.options['protocol_configuration']['events_per_level'])\
                  /master_fsm.options['generator_configuration']['rate']
        timeout+=1.
        if not run_level(master_fsm,timeout):
            log.error('Failed at level %d'%level)
            return False
        pbar.update(1)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('AC')

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True



    def loop_over_ac_pixels(self, level, timeout=0.05, n_triggers=10, frequency = 1000 , start_pixel = None, stop_pixel = None):
        """
        loop_over_ac_pixels(level,timeout,trigger,n_trigger)

        A function to light AC pixels one after the other in increasing software pixel id

        Inputs :
                 - level   : the DAC level to apply (int)
                 - timeout : the amount of time, in s, to keep the pixels on (float)
                 - n_trigger : number of consecutive trigger for AC
                 - start_pixel : the first pixel of the sequence
                 - stop_pixel : the last pixel of the sequence
        """
        # Initialise the trigger
        self.generator.configure_trigger(n_pulse = n_triggers, freq= frequency)
        # loop over the patches to set the DAC level
        for patch in self.cts.LED_patches:
            self.cts_client.set_ac_level(patch.camera_patch_id, level)
        # loop over the pixels
        pixel_list = list(self.cts.pixel_to_led['AC'].keys())
        pixel_list.sort()
        for i, pix in enumerate(pixel_list):
            if start_pixel and pix < start_pixel :continue
            if stop_pixel and pix > stop_pixel :continue
            if i > 0:
                # turn off the previous pixel
                self.cts_client.set_led_status('AC', pixel_list[i - 1], False)
                self.ac_status[pixel_list[i - 1]] = 0
                self.ac_level[pixel_list[i - 1]] = 0
            time.sleep(timeout)
            # turn on this pixel
            self.cts_client.set_led_status('AC', pixel_list[i], True)
            self.ac_status[pixel_list[i]] = 1
            self.ac_level[pixel_list[i]] = level
            self.generator.start_trigger_sequence()
            if self.plotting:
                self.plot()
            time.sleep(timeout)
        # turn off the last pixel
        self.cts_client.set_led_status('AC', pixel_list[-1], False)
        self.ac_status[pixel_list[-1]] = 0
        # loop over hte patches and put the DAC back to 0
        for patch in self.cts.LED_patches:
            self.cts_client.set_ac_level(patch.camera_patch_id, 0)
            self.ac_level[pixel_list[-1]] = level
        # put back the default trigger configruation
        self.generator.stop_trigger_sequence()
