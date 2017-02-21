import fysom
import logging
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger

protocol_name = 'SIMPLE_DAQ'

def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('Start the '+protocol_name+' protocol')

    if not allocate(master_fsm): return False
    if not configure(master_fsm): return False
    if not start_run(master_fsm): return False
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

    if not stop_trigger(master_fsm): return False
    if not stop_run(master_fsm): return False
    if not reset(master_fsm): return False
    if not deallocate(master_fsm): return False


    log.info('Ended the '+protocol_name+' protocol')


    return True


