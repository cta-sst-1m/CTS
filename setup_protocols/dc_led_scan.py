import logging,sys,fysom,time
from setup_protocols.fsm_steps import *
from tqdm import tqdm
from utils.logger import TqdmToLogger

protocol_name = 'AC_LED_SCAN'

def prepare_run(master_fsm):
    '''

    :param master_fsm:
    :return:
    '''

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('Start the '+protocol_name+' protocol')

    if not allocate(master_fsm): return False
    if not configure(master_fsm): return False
    if not start_run(master_fsm): return False


    log.info('Elements of the setup have been allocated, the Camera server has started and the ZFits writer too')
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
    log.info('Ended the '+protocol_name+' protocol')
    return True



def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    master_fsm['generator_configuration']['number_of_pulses'] =  \
        master_fsm['protocol_configuration']['events_per_level']

    master_fsm['writer_configuration']['max_evts_per_file'] = \
        master_fsm['protocol_configuration']['events_per_level']*10

    if not prepare_run(master_fsm):
        log.error('Failed to prepare the '+protocol_name+' run')
        return False

    # Turn on the DC LEDs
    master_fsm.elements['cts_core'].all_on('DC',0)
    if 'ac_level' in master_fsm['protocol_configuration'].keys():
        master_fsm.elements['cts_core'].all_on('AC',0)
        level = master_fsm['protocol_configuration']['ac_level']
        log.debug('  -|> Set AC Level to %d' % level)
        for patch in master_fsm.elements['cts_core'].cts.LED_patches:
            master_fsm.elements['cts_core'].cts_client.set_ac_level(patch.camera_patch_id, level)

    DC_DAC_Levels = master_fsm['protocol_configuration']['levels']

    pbar = tqdm(total=len(DC_DAC_Levels))
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    for i,level in DC_DAC_Levels :
        for board in master_fsm.elements['cts_core'].cts.LED_boards:
            master_fsm.elements['cts_core'].cts_client.set_dc_level(board.internal_id, level)

        timeout = master_fsm['protocol_configuration']['events_per_level']\
                  /master_fsm['generator_configuration']['rate']
        if not run_level(master_fsm,timeout):
            log.error('Failed at level %d'%level)
            return False
        pbar.update(1)

    # Turn off the AC LEDs
    master_fsm.elements['cts_core'].all_off('DC',0)
    if 'ac_level' in master_fsm['protocol_configuration'].keys():
        master_fsm.elements['cts_core'].all_off('AC', 0)

    if not end_run(master_fsm):
        log.error('Failed to terminate the '+protocol_name+' run')
        return False

    return True