import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger

protocol_name = 'DC_MAPPING_SCAN'

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
        log.error('Failed to prepare the DC LED SCAN run')
        return False

    # Turn on the AC LEDs0
    #master_fsm.elements['cts_core'].all_off('AC')
    # Get the AC LEDs level to run
    ac_level = master_fsm.options['protocol_configuration']['dc_level']

    # Define the progress bar
    log.info('\033[1m\033[91m\t\t-|> Start the DC Mapping loop\033[0m' )
    pbar = tqdm(total=528)
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    for board in master_fsm.elements['cts_core'].cts.LED_boards:
        master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, ac_level)
    # loop over the pixels
    pixel_list = list(master_fsm.elements['cts_core'].cts.pixel_to_led['DC'].keys())
    pixel_list.sort()

    if 'pixel_list' in master_fsm.options['protocol_configuration']:
        pixel_list = master_fsm.options['protocol_configuration']['pixel_list']

    for i, pix in enumerate(pixel_list):
        if start_pixel and pix < start_pixel: continue
        if stop_pixel and pix > stop_pixel: continue
        if i > 0:
            # turn off the previous pixel
            master_fsm.elements['cts_core'].cts_client.set_led_status('DC', pixel_list[i - 1], False)
            master_fsm.elements['cts_core'].dc_status[pixel_list[i - 1]] = 0
            master_fsm.elements['cts_core'].dc_level[pixel_list[i - 1]] = 0
        # turn on this pixel
        master_fsm.elements['cts_core'].cts_client.set_led_status('DC', pixel_list[i], True)
        master_fsm.elements['cts_core'].dc_status[pixel_list[i]] = 1
        master_fsm.elements['cts_core'].dc_level[pixel_list[i]] = ac_level

        log.debug('\033[1m\033[91m\t\t-|> Pixel%d\033[0m' % pix)
        if not run_level(master_fsm,0.01):
            log.error('Failed at Pixel %d'%pix)
            return False
        pbar.update(1)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('DC')

    # And finalise the run
    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True
