import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger

protocol_name = 'AC_MAPPING_SCAN'

def prepare_run(master_fsm):
    '''

    :param master_fsm:
    :return:
    '''

    log = logging.getLogger(sys.modules['__main__'].__name__)

    log.info('\033[1m\033[91m\t\t-|> Start the %s Protocol\033[0m'%protocol_name)

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
    log.info('\033[1m\033[91m\t\t-|> End the %s Protocol\033[0m'%protocol_name)
    return True



def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    start_pixel = None
    stop_pixel = None

    # Some preliminary configurations
    master_fsm.options['generator_configuration']['number_of_pulses'] =  1

    if 'writer_configuration' in master_fsm.options : master_fsm.options['writer_configuration']['max_evts_per_file'] = 2000

    # Call the FSMs transition to start the run
    if not prepare_run(master_fsm):
        log.error('Failed to prepare the AC LED SCAN run')
        return False

    # Turn on the AC LEDs0
    #master_fsm.elements['cts_core'].all_off('AC')
    # Get the AC LEDs level to run
    ac_level = master_fsm.options['protocol_configuration']['ac_level']

    # Define the progress bar
    log.info('\033[1m\033[91m\t\t-|> Start the AC Mapping loop\033[0m' )
    pbar = tqdm(total=176)
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    for patch in master_fsm.elements['cts_core'].cts.LED_patches:
        master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, ac_level)

    patch_list = list(master_fsm.elements['cts_core'].cts.patch_camera_to_patch_led.keys())
    patch_list.sort()

    for i, patch in enumerate(patch_list):
        ledpatch = master_fsm.elements['cts_core'].cts.LED_patches[master_fsm.elements['cts_core'].cts.patch_camera_to_patch_led[patch]]
        if i > 0:
            # turn off the previous patch
            ledpatch_prev = master_fsm.elements['cts_core'].cts.LED_patches[
                master_fsm.elements['cts_core'].cts.patch_camera_to_patch_led[patch_list[i - 1]]]
            for pix in ledpatch_prev.leds_camera_pixel_id:
                master_fsm.elements['cts_core'].cts_client.set_led_status('AC', pix, False)
            # put back the DAC level to 0
            master_fsm.elements['cts_core'].cts_client.set_ac_level(patch, 0)
        # turn on the present patch
        for pix in ledpatch.leds_camera_pixel_id:
            master_fsm.elements['cts_core'].cts_client.set_led_status('AC', pix, True)
        # turn on the DAC level
        master_fsm.elements['cts_core'].cts_client.set_ac_level(patch, ac_level)
        log.debug('\033[1m\033[91m\t\t-|> Patch%d\033[0m' % patch)
        if not run_level(master_fsm,0.1):
            log.error('Failed at Patch %d'%pix)
            return False
        pbar.update(1)

    # turn off last patch
    for pix in master_fsm.elements['cts_core'].cts.LED_patches[master_fsm.elements['cts_core'].cts.patch_camera_to_patch_led[patch_list[-1]]].leds_camera_pixel_id:
        master_fsm.elements['cts_core'].cts_client.set_led_status('AC', pix, False)
    # set back the level to 0
    for patch in master_fsm.elements['cts_core'].cts.LED_patches:
        master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, 0)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('AC')

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True
