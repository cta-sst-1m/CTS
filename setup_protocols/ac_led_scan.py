import fysom
import logging
import sys
import time
from tqdm import tqdm
import utils.led_calibration as led_calib

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
    levels_in_pe = 'levels_in_pe' in master_fsm.options['protocol_configuration'].keys() and master_fsm.options['protocol_configuration']['levels_in_pe']

    # Define the progress bar
    log.info('\033[1m\033[91m\t\t-|> Start the AC DAC level loop\033[0m' )
    pbar = tqdm(total=len(AC_DAC_Levels))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    levels_log = []
    patches = master_fsm.elements['cts_core'].cts.LED_patches \
        if 'patches' not in master_fsm.options['protocol_configuration'].keys() \
        else [ p.internal_id for p in master_fsm.elements['cts_core'].cts.LED_patches
               if p.camera_patch_id in master_fsm.options['protocol_configuration']['patches']]

    for i,level in enumerate(AC_DAC_Levels) :
        levels_log.append([])
        for patch in patches:
            _level =  led_calib.get_ACPATCH_DAC_byled(level,patch.internal_id) if levels_in_pe else level
            levels_log[-1].append('pixel patch %d, led patch %d , DAC %d'%(patch.camera_patch_id,patch.internal_id,_level))
            master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, _level if levels_in_pe else level)

        log.debug('\033[1m\033[91m\t\t-|> Level%d\033[0m' % level)
        timeout = float(master_fsm.options['protocol_configuration']['events_per_level'])\
                  /master_fsm.options['generator_configuration']['rate']
        timeout+=1.
        if not run_level(master_fsm,timeout):
            log.error('Failed at level %d'%level)
            return False
        pbar.update(1)

    for i,ll in enumerate(levels_log):
        log.debug('############################## LEVEL %d'%AC_DAC_Levels[i])
        for l in ll:
            log.debug(l)


    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('AC')

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True