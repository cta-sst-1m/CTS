import logging,sys,fysom,time

def prepare_run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('Start the MTS protocol')

    # ALLOCATE
    try:
        master_fsm.allocate()
    except fysom.Canceled:
        log.warning('MASTER could not be alocated')
        return False
    except fysom.Error:
        log.error('MASTER was not in the proer state')
        return False

    log.info('Elements of the setup have been allocated and Camera server started')
    return True

def end_run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    # ALLOCATE
    try:
        master_fsm.deallocate()
    except fysom.Canceled:
        log.warning('MASTER could not be dealocated')
        return False
    except fysom.Error:
        log.error('MASTER was not in the proer state')
        return False

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

    # CONFIGURE FOR WRITER
    master_fsm.options['writer_configuration']['max_evts_per_file'] =\
        master_fsm.options['protocol_configuration']['%s_number_of_events'%sub_run]

    # NOW CONFIGURE THE GENERATOR SLAVE FOR THE LIGHT LEVEL
    offset = master_fsm.options['protocol_configuration']['%s_level'%sub_run] / 2
    master_fsm.options['generator_configuration']['slave_amplitude']= master_fsm.options['protocol_configuration']['%s_level'%sub_run]
    master_fsm.options['generator_configuration']['slave_offset'] = -1.*offset

    try:
        master_fsm.configure()
    except fysom.Canceled:
        log.warning('MASTER could not be configured')
        master_fsm.abort()
        return False
    except fysom.Error:
        log.error('MASTER was not in the proper state')
        master_fsm.abort()
        return False


    # START_RUN FOR LOW LIGHT
    try:
        master_fsm.start_run()
    except fysom.Canceled:
        log.warning('MASTER could not start run')
        master_fsm.abort()
        return False
    except fysom.Error:
        log.error('MASTER was not in the proper state')
        master_fsm.abort()
        return False


    # START_TRIGGER FOR LOW LIGHT
    try:
        master_fsm.start_trigger()
    except fysom.Canceled:
        log.warning('MASTER could not start trigger')
        master_fsm.abort()
        return False
    except fysom.Error:
        log.error('MASTER was not in the proper state')
        master_fsm.abort()
        return False

    timeout = float(master_fsm.options['protocol_configuration']['%s_number_of_events'%sub_run])\
              /master_fsm.options['generator_configuration']['frequency']+2

    time.sleep(timeout)

    try:
        master_fsm.stop_trigger()
    except fysom.Canceled:
        log.warning('MASTER could not start trigger')
        master_fsm.abort()
        return False
    except fysom.Error:
        log.error('MASTER was not in the proper state')
        master_fsm.abort()
        return False


    try:
        master_fsm.stop_run()
    except fysom.Canceled:
        log.warning('MASTER could not start trigger')
        master_fsm.abort()
        return False
    except fysom.Error:
        log.error('MASTER was not in the proper state')
        master_fsm.abort()
        return False

    try:
        master_fsm.reset()
    except fysom.Canceled:
        log.warning('MASTER could not reset master')
        master_fsm.abort()
        return False
    except fysom.Error:
        log.error('MASTER was not in the proper state')
        master_fsm.abort()
        return False

    return True



def run(master_fsm):

    log = logging.getLogger(sys.modules['__main__'].__name__)

    if not prepare_run(master_fsm):
        log.error('Failed to prepare the MTS run')
        return False
    for l in ['low','medium','high']:
        if not single_run(master_fsm, sub_run='%s_light'%l):
            log.error('Failed to run the %s light MTS'%l)
            return False

    if not end_run(master_fsm):
        log.error('Failed to terminate the MTS run')
        return False

    return True