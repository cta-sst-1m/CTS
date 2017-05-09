
import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger


import utils.led_calibration as led_calib

protocol_name = 'DC_LED_SCAN'

def prepare_run(master_fsm):
    '''

    :param master_fsm:
    :return:
    '''

    log = logging.getLogger(sys.modules['__main__'].__name__)

    log.info('\033[1m\033[91m\t\t-|> Start the DC LED SCAN Protocol\033[0m')

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
    log.info('\033[1m\033[91m\t\t-|> End the DC LED SCAN Protocol\033[0m')
    return True



def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    # Some preliminary configurations
    master_fsm.options['generator_configuration']['number_of_pulses'] =  \
        master_fsm.options['protocol_configuration']['events_per_level']

    master_fsm.options['writer_configuration']['max_evts_per_file'] = \
        master_fsm.options['protocol_configuration']['events_per_level']*10

    # Call the FSMs transition to start the run
    if not prepare_run(master_fsm):
        log.error('Failed to prepare the AC LED SCAN run')
        return False



    # Turn on the DC LEDs
    master_fsm.elements['cts_core'].all_on('DC',0)
    if 'ac_level' in master_fsm.options['protocol_configuration'].keys():
        master_fsm.elements['cts_core'].all_on('AC',0)
        level = master_fsm.options['protocol_configuration']['ac_level']

        log.info('\033[1m\033[91m\t\t-|>Set AC Level to %d\033[0m' % level)
        for patch in master_fsm.elements['cts_core'].cts.LED_patches:
            master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, level)

    DC_DAC_Levels = master_fsm.options['protocol_configuration']['levels']
    levels_in_pe = 'levels_in_pe' in master_fsm.options['protocol_configuration'].keys() and \
                   master_fsm.options['protocol_configuration']['levels_in_pe']

    log.info('\033[1m\033[91m\t\t-|> Start the DAC level loop\033[0m' )
    pbar = tqdm(total=len(DC_DAC_Levels))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    for i,level in enumerate(DC_DAC_Levels) :
        log.debug('\033[1m\033[91m\t\t-|> Level%d\033[0m' % level)
        for board in master_fsm.elements['cts_core'].cts.LED_boards:
            _level =  led_calib.get_DCBOARD_DAC_byled(patch.internal_id,level*48) if levels_in_pe else level
            log.debug('pixel board %d, led board %d , DAC %d'%( master_fsm.elements['cts_core'].cts.camera.Pixels[board.leds_camera_pixel_id[0]].fadc_unique,
                                                                 patch.internal_id,_level))
            master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, _level)
        time.sleep(1)
        timeout = master_fsm.options['protocol_configuration']['events_per_level']\
                  /master_fsm.options['generator_configuration']['rate']
        timeout+=2.
        if not run_level(master_fsm,timeout):
            log.error('Failed at level %d'%level)
            return False
        pbar.update(1)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('DC')
    if 'ac_level' in master_fsm.options['protocol_configuration'].keys():
        master_fsm.elements['cts_core'].all_off('AC')

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True
