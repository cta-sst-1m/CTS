import fysom
import logging
import sys
import time
from tqdm import tqdm

import utils.led_calibration as led_calib

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger

protocol_name = 'SIMPLE_DAQ'

def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('Start the '+protocol_name+' protocol')

    if not allocate(master_fsm): return False
    if not configure(master_fsm): return False
    if not start_run(master_fsm): return False

    dc_level,ac_level,levels_in_pe = None,None,None
    if 'cts_configuration' in master_fsm.options.keys():
        dc_level = master_fsm.options['protocol_configuration']['dc_level']
        ac_level = master_fsm.options['protocol_configuration']['ac_level']
        levels_in_pe = 'levels_in_pe' in master_fsm.options['protocol_configuration'].keys() and \
                       master_fsm.options['protocol_configuration']['levels_in_pe']

        for patch in master_fsm.elements['cts_core'].cts.LED_patches:
            _ac_level =  led_calib.get_ACPATCH_DAC_byled(patch.internal_id,ac_level*3) if levels_in_pe else ac_level
            log.append('pixel patch %d, led patch %d , DAC %d'%(patch.camera_patch_id,patch.internal_id,_ac_level))
            master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, _ac_level)

        for board in master_fsm.elements['cts_core'].cts.LED_boards:
            _dc_level = led_calib.get_DCBOARD_DAC_byled(patch.internal_id,
                                                        dc_level * 48) if levels_in_pe else dc_level
            log.debug('DC: pixel board %d, led board %d , DAC %d' % (
                master_fsm.elements['cts_core'].cts.camera.Pixels[board.leds_camera_pixel_id[0]].fadc_unique,
                patch.internal_id, dc_level))
            master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, _dc_level)


    if not start_trigger(master_fsm): return False
    timeout = 0.
    if master_fsm.options['camera_configuration']['trigger_configuration']=='external':
        timeout = float(master_fsm.options['protocol_configuration']['number_of_events'])\
                 /master_fsm.options['generator_configuration']['rate']+2
    else :
        timeout = float(master_fsm.options['protocol_configuration']['number_of_events'])\
                 /master_fsm.options['camera_configuration']['rate']+2

    pbar = tqdm(total=int(timeout))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    i=0
    while i < timeout:
        time.sleep(1)
        pbar.update(1)
        i+=1

    if not stop_trigger(master_fsm): return False

    if 'cts_configuration' in master_fsm.options.keys():
        master_fsm.elements['cts_core'].all_off('AC')
        master_fsm.elements['cts_core'].all_off('DC')

    if not stop_run(master_fsm): return False
    if not reset(master_fsm): return False
    if not deallocate(master_fsm): return False


    log.info('Ended the '+protocol_name+' protocol')


    return True


