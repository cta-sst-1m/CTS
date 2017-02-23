import logging
import subprocess
import sys
import time
from tqdm import tqdm

from setup_fsm.fsm_steps import *
from utils.logger import TqdmToLogger


def prepare_run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)


    log.info('\033[1m\033[91m\t\t-|> Start the MTS Protocol\033[0m')

    # ALLOCATE
    if not allocate(master_fsm): return False
    if not configure(master_fsm): return False

    return True

def end_run(master_fsm):
    """

    :param master_fsm:
    :return:
    """

    log = logging.getLogger(sys.modules['__main__'].__name__)
    if not reset(master_fsm): return False
    if not deallocate(master_fsm): return False
    log.info('\033[1m\033[91m\t\t-|> End the MTS Protocol\033[0m')
    return True

def single_run(master_fsm,sub_run= 'low_light'):
    """

    master_fsm should contain the following 'cts_configuration' options:

    (sub_run)_level
    (sub_run)_number_of_eventss

    :param master_fsm: the master FSM
    :param sub_run:    the sub_run name
    :return:
    """

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('\033[1m\033[91m\t\t-|> Process %s step\033[0m'%sub_run)

    # CONFIGURE FOR WRITER
    master_fsm.options['writer_configuration']['max_evts_per_file'] =\
        master_fsm.options['protocol_configuration']['%s_number_of_events'%sub_run]

    # NOW CONFIGURE THE GENERATOR SLAVE FOR THE LIGHT LEVEL
    offset = master_fsm.options['protocol_configuration']['%s_level'%sub_run] / 2
    master_fsm.options['generator_configuration']['slave_amplitude']= master_fsm.options['protocol_configuration']['%s_level'%sub_run]
    master_fsm.options['generator_configuration']['slave_offset'] = 1.*offset

    if not start_run(master_fsm): return False
    if not start_trigger(master_fsm): return False

    timeout = float(master_fsm.options['protocol_configuration']['%s_number_of_events'%sub_run])\
              /master_fsm.options['generator_configuration']['rate']

    pbar = tqdm(total=int(timeout))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    i=0
    while i < timeout:
        time.sleep(1)
        pbar.update(1)
        i+=1

    if not stop_trigger(master_fsm): return False
    time.sleep(2)
    if not stop_run(master_fsm): return False

    return True



def run(master_fsm):
    """
    The main function of the protocol

    :param master_fsm:
    :return:
    """

    log = logging.getLogger(sys.modules['__main__'].__name__)

    # First prepare call the FSMs which will be called once only
    if not prepare_run(master_fsm):
        log.error('Failed to prepare the MTS run')
        return False
    # Now move to the various runs
    # Get the run names:
    run_set = set()
    for run in master_fsm.options['protocol_configuration']:
        if run == 'name': continue
        run_set.add(run.split('_')[0])
    for l in run_set:
        if not single_run(master_fsm, sub_run='%s_light'%l):
            log.error('Failed to run the %s light MTS'%l)
            return False

    # And finalise
    if not end_run(master_fsm):
        log.error('Failed to terminate the MTS run')
        return False

    return True