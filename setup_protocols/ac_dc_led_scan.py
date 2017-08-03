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
    master_fsm.elements['cts_core'].all_on('DC',0)
    # Get the AC LEDs level to run
    AC_DAC_Levels = master_fsm.options['protocol_configuration']['ac_levels']
    DC_DAC_Levels = master_fsm.options['protocol_configuration']['dc_levels']
    levels_in_pe = 'levels_in_pe' in master_fsm.options['protocol_configuration'].keys() and master_fsm.options['protocol_configuration']['levels_in_pe']
    levels_in_nsb = 'levels_in_nsb' in master_fsm.options['protocol_configuration'].keys() and master_fsm.options['protocol_configuration']['levels_in_nsb']

    # Define the progress bar
    log.info('\033[1m\033[91m\t\t-|> Start the AC DAC level loop\033[0m' )
    pbar = tqdm(total=len(AC_DAC_Levels)*len(DC_DAC_Levels))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    levels_log = []
    patches = master_fsm.elements['cts_core'].cts.LED_patches \
        if 'patches' not in master_fsm.options['protocol_configuration'].keys() \
        else [ p for p in master_fsm.elements['cts_core'].cts.LED_patches
               if p.camera_patch_id in master_fsm.options['protocol_configuration']['patches']]

    boards = master_fsm.elements['cts_core'].cts.LED_boards \
        if 'boards' not in master_fsm.options['protocol_configuration'].keys() \
        else [p for p in master_fsm.elements['cts_core'].cts.LED_boards
              if p.internal_id in master_fsm.options['protocol_configuration']['boards']]

    levels_log = []
    for i, dc_level in enumerate(DC_DAC_Levels):
        ### Loop over the AC levels (which can be by pe or by DAC)
        for i, ac_level in enumerate(AC_DAC_Levels):
            # Check if it is required to run some dark in betw
            level_pairs_list = [[0, 0], [ac_level, dc_level]] \
                if master_fsm.options['protocol_configuration']['events_per_level_check'] > 0 \
                else [[ac_level, dc_level]]

            for level_check,level_pairs in enumerate(level_pairs_list):
                levels_log.append(['############################## LEVEL AC: %d DC: %d'%(level_pairs[0],level_pairs[1])])
                list_of_level = ''
                for board in boards:
                    _dc_level = led_calib.get_DCBOARD_DAC(level_pairs[1],
                                                          master_fsm.elements['cts_core'].cts.camera.Pixels[
                                                              board.leds_camera_pixel_id[
                                                                  0]].fadc_unique) if levels_in_nsb else level_pairs[1]
                    master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, _dc_level)
                    list_of_level += 'Board: %d | DC:%d' % (board.internal_id, _dc_level)
                    levels_log[-1].append(
                        'led board %d , DAC %d' % (board.leds_camera_pixel_id[0], _dc_level))

                for patch in patches:
                    _ac_level = led_calib.get_ACPATCH_DAC(level_pairs[0], patch.camera_patch_id) if levels_in_pe else \
                    level_pairs[0]
                    master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, _ac_level)
                    list_of_level += 'Patch %d | AC:%d' % (patch.camera_patch_id, _ac_level)
                    levels_log[-1].append(
                        'pixel patch %d, led patch %d , DAC %d' % (patch.camera_patch_id, patch.internal_id, _ac_level))

                log.debug('\033[1m\033[91m\t\t-|> Level %d %d\033[0m' % (_ac_level,_dc_level))
                log.debug(list_of_level)
                evt_per_level = master_fsm.options['protocol_configuration'][
                    'events_per_level'] if level_check == 1 else \
                    master_fsm.options['protocol_configuration']['events_per_level_check']
                timeout = float(evt_per_level) \
                          / master_fsm.options['generator_configuration']['rate']
                timeout += 1.
                if not run_level(master_fsm, timeout):
                    log.error('Failed at level %d %d' %  (_ac_level,_dc_level))
                    return False
                pbar.update(1)

    for i,ll in enumerate(levels_log):
        #log.debug('############################## LEVEL %d %d'%AC_DAC_Levels[i])
        for l in ll:
            log.debug(l)


    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('AC')
    master_fsm.elements['cts_core'].all_off('DC')

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True