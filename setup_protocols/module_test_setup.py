from setup_protocols.fsm_steps import *
import logging,sys,time
from tqdm import tqdm
from utils.logger import TqdmToLogger
import subprocess

def prepare_run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('Start the MTS protocol')

    # ALLOCATE

    log.info('Elements of the setup have been allocated and Camera server started')
    return True

def end_run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)


    log.info('Ended the MTS protocol')
    return True

def single_run(master_fsm,sub_run= 'low_light'):
    """

    master_fsm should contain the following 'cts_configuration' options:

    low_light_level
    low_light_number_of_events
    medium_light_level
    medium_light_number_of_events
    high_light_level
    high_light_number_of_events


    :param master_fsm:
    :return:
    """

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('Process %s step'%sub_run)

    if not allocate(master_fsm): return False
    # CONFIGURE FOR WRITER
    master_fsm.options['writer_configuration']['max_evts_per_file'] =\
        master_fsm.options['protocol_configuration']['%s_number_of_events'%sub_run]

    # NOW CONFIGURE THE GENERATOR SLAVE FOR THE LIGHT LEVEL
    offset = master_fsm.options['protocol_configuration']['%s_level'%sub_run] / 2
    master_fsm.options['generator_configuration']['slave_amplitude']= master_fsm.options['protocol_configuration']['%s_level'%sub_run]
    master_fsm.options['generator_configuration']['slave_offset'] = 1.*offset

    if not configure(master_fsm): return False
    if not start_run(master_fsm): return False
    time.sleep(2.)

    if not start_trigger(master_fsm): return False

    timeout = float(master_fsm.options['protocol_configuration']['%s_number_of_events'%sub_run])\
              /master_fsm.options['generator_configuration']['rate']+2

    pbar = tqdm(total=int(timeout))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    i=0
    while i < timeout:
        time.sleep(1)
        pbar.update(1)
        i+=1

    if not stop_trigger(master_fsm): return False
    if not stop_run(master_fsm): return False
    if not reset(master_fsm): return False
    if not deallocate(master_fsm): return False
    time.sleep(2)

    return True



def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    if not prepare_run(master_fsm):
        log.error('Failed to prepare the MTS run')
        return False
    for l in ['dark','low','medium','high']:
        if not single_run(master_fsm, sub_run='%s_light'%l):
            log.error('Failed to run the %s light MTS'%l)
            return False
        #err = subprocess.check_output('ps - A | grep riter',shell=True)
        #print('================================================ %s ==============================='%err)
        time.sleep(2)
    '''
    if not end_run(master_fsm):
        log.error('Failed to terminate the MTS run')
        return False
    '''
    return True