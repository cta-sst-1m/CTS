
import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger
import utils.led_calibration as led_calib

protocol_name = 'ACDC_LED_SCAN'

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
    master_fsm.elements['cts_core'].all_on('AC',0)


    DC_DAC_Levels = master_fsm.options['protocol_configuration']['dc_levels']
    AC_DAC_Levels = master_fsm.options['protocol_configuration']['ac_levels']

    levels_in_pe = 'levels_in_pe' in master_fsm.options['protocol_configuration'].keys() and master_fsm.options['protocol_configuration']['levels_in_pe']
    levels_in_nsb = 'levels_in_nsb' in master_fsm.options['protocol_configuration'].keys() and master_fsm.options['protocol_configuration']['levels_in_nsb']


    log.info('\033[1m\033[91m\t\t-|> Start the DAC level loop\033[0m' )
    pbar = tqdm(total=len(DC_DAC_Levels)*len(AC_DAC_Levels))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    patches = master_fsm.elements['cts_core'].cts.LED_patches \
        if 'patches' not in master_fsm.options['protocol_configuration'].keys() \
        else [ p for p in master_fsm.elements['cts_core'].cts.LED_patches
               if p.camera_patch_id in master_fsm.options['protocol_configuration']['patches']]

    boards = master_fsm.elements['cts_core'].cts.LED_boards \
        if 'boards' not in master_fsm.options['protocol_configuration'].keys() \
        else [ p for p in master_fsm.elements['cts_core'].cts.LED_boards
               if p.internal_id in master_fsm.options['protocol_configuration']['boards']]
    levels_log = []
    for i,dc_level in enumerate(DC_DAC_Levels) :
        for board in boards:
            _dc_level =  led_calib.get_DCBOARD_DAC(dc_level,cts.camera.Pixels[board.leds_camera_pixel_id[0]].fadc_unique) if levels_in_nsb else dc_level
            master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, _dc_level if levels_in_pe else dc_level)

        for j, ac_level in enumerate(AC_DAC_Levels):
            levels_log.append([])
            for patch in patches:
                _ac_level =  led_calib.get_ACPATCH_DAC(ac_level,patch.camera_patch_id) if levels_in_pe else ac_level
                levels_log[-1].append('pixel patch %d, led patch %d , DAC %d'%(patch.camera_patch_id,patch.internal_id,_ac_level))
                master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, _ac_level if levels_in_pe else ac_level)

            timeout = master_fsm.options['protocol_configuration']['events_per_level'] \
                      / master_fsm.options['generator_configuration']['rate']
            timeout += 1.
            if not run_level(master_fsm, timeout):
                log.error('Failed at level DC %d AC %d' % (dc_level,ac_level))
                return False
            pbar.update(1)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('DC',0)
    if 'ac_level' in master_fsm.options['protocol_configuration'].keys():
        master_fsm.elements['cts_core'].all_off('AC', 0)

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True
