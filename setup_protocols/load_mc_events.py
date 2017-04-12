
import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger
import numpy as np

protocol_name = 'LOAD_MC_EVENTS'

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
    log.info('\033[1m\033[91m\t\t-|> End the %s\033[0m'%(protocol_name))
    return True



'''
def load_mc_event(evt_number,mc_events,master_fsm,param):
    pixel_values = mc_events[evt_number]
    for patch in master_fsm.elements['cts_core'].cts.LED_patches:
        pe_in_pixels = []
        for pix in patch.leds_camera_pixel_id:
            pe_in_pixels+=[pixel_values[pix]]
        level = get_patch_DAC(patch.leds_camera_pixel_id,pe_in_pixels,param)
        master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, level)

    return
'''
def load_led_parameters(master_fsm):
    ac_led_coefficient = np.load( master_fsm.options['protocol_configuration']['led_parameters_file'])['fit_result']
    param, covariance = ac_led_coefficient[:, :, 0], ac_led_coefficient[:, :, 2:7:1]
    return param

def get_patch_DAC(pixels,pe_per_pixel,param):
    dac = 0
    total_pe = np.sum(pe_per_pixel)
    sum_param = np.zeros(param.shape[-1],dtype=param.dtype)
    for p in pixels:
        sum_param= sum_param+param[p]

    inv_p = lambda y: np.max(np.real((np.poly1d(sum_param) - y).roots))
    return inv_p(total_pe)




def load_mc_event(pixel_values,pixel_list,master_fsm,param):
    patch_dac,patch_pe = [],[]
    for patch in master_fsm.elements['cts_core'].cts.LED_patches:
        pe_in_pixels = []
        for pix in patch.leds_camera_pixel_id:
            pe_in_pixels+=[pixel_values[pix]]
        dac=get_patch_DAC(patch.leds_camera_pixel_id, pixel_list,pe_in_pixels, param)
        master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, dac)
        pe = np.mean(pe_in_pixels)
        patch_dac.append(dac)
        patch_pe.append(pe)
    return patch_dac,patch_pe


def get_patch_DAC(pixels,pixel_list,pe_per_pixel,param):
    dac = 0
    total_pe = np.sum(pe_per_pixel)
    if total_pe==0.: return 0.
    sum_param = np.zeros(param.shape[-1],dtype=param.dtype)
    for p in pixels:
        sum_param= sum_param+param[pixel_list.index(p)]
    dac = 0
    try:
        dac = np.max(np.real((np.poly1d(sum_param) - total_pe).roots))
    except:
        dac = -1
    return int(np.round(dac))




def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    # Some preliminary configurations
    master_fsm.options['generator_configuration']['number_of_pulses'] =  \
        master_fsm.options['protocol_configuration']['events_per_mc_event']

    master_fsm.options['writer_configuration']['max_evts_per_file'] = \
        master_fsm.options['protocol_configuration']['events_per_mc_event']*10

    # load the AC led calibration parameters
    ac_led_coefficient = np.load(master_fsm.options['protocol_configuration']['led_parameters_file'])['fit_result']
    param, covariance = ac_led_coefficient[:, :, 0], ac_led_coefficient[:, :, 2:7:1]


    # Call the FSMs transition to start the run
    if not prepare_run(master_fsm):
        log.error('Failed to prepare the AC LED SCAN run')
        return False



    # Turn on the DC and AC LEDs
    master_fsm.elements['cts_core'].all_on('DC',0)
    master_fsm.elements['cts_core'].all_on('AC',0)


    dc_level = master_fsm.options['protocol_configuration']['dc_level']
    mc_events_file_path = master_fsm.options['protocol_configuration']['mc_events_file']
    N_mc_events = master_fsm.options['protocol_configuration']['N_mc_events']

    # load the mc events
    mc_events = np.load(mc_events_file_path)

    pixel_list = []
    for pix in master_fsm.elements['cts_core'].cts.camera.Pixels:
        if pix.ID in master_fsm.elements['cts_core'].cts.pixel_to_led['AC'].keys():
            pixel_list.append(pix.ID)

    log.info('\033[1m\033[91m\t\t-|> Start the DAC level loop\033[0m' )
    pbar = tqdm(total=len(N_mc_events))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    for board in master_fsm.elements['cts_core'].cts.LED_boards:
        master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, dc_level )

    for i in N_mc_events :
        load_mc_event(mc_events[i], pixel_list, master_fsm, param)
        timeout = master_fsm.options['protocol_configuration']['events_per_mc_event'] \
                  / master_fsm.options['generator_configuration']['rate']
        timeout += 1.
        if not run_level(master_fsm, timeout):
            log.error('Failed at event %d' % i)
            return False
        pbar.update(1)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('DC',0)
    master_fsm.elements['cts_core'].all_off('AC', 0)

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True
