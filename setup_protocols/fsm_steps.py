import fysom,logging,sys

__all__= ['allocate','configure','start_run','start_trigger','stop_trigger','stop_run','reset','deallocate','abort']


def allocate(master_fsm):
    '''
    Allocate the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('ALLOCATE canceled, go back to UNALLOCATED state')
        return False
    except fysom.Error:
        log.error('ALLOCATE could not be performed, wrong input state')
        return False
    return True



def configure(master_fsm):
    '''
    Configure the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('CONFIGURE canceled, go back to NOT_READY state')
        return False
    except fysom.Error:
        log.error('CONFIGURE could not be performed, wrong input state')
        return False
    return True



def start_run(master_fsm):
    '''
    start_run the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('START_RUN canceled, go back to READY state')
        return False
    except fysom.Error:
        log.error('START_RUN could not be performed, wrong input state')
        return False
    return True



def start_trigger(master_fsm):
    '''
    start_trigger the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('START_TRIGGER canceled, go back to STAND_BY state')
        return False
    except fysom.Error:
        log.error('START_TRIGGER could not be performed, wrong input state')
        return False
    return True



def stop_trigger(master_fsm):
    '''
    start_trigger the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('STOP_TRIGGER canceled, go back to RUNNING state')
        return False
    except fysom.Error:
        log.error('STOP_TRIGGER could not be performed, wrong input state')
        return False
    return True


def stop_run(master_fsm):
    '''
    stop_run the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('STOP_RUN canceled, go back to STAND_BY state')
        return False
    except fysom.Error:
        log.error('STOP_RUN could not be performed, wrong input state')
        return False
    return True


def reset(master_fsm):
    '''
    reset the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('RESET canceled, go back to READY state')
        return False
    except fysom.Error:
        log.error('RESET could not be performed, wrong input state')
        return False
    return True


def deallocate(master_fsm):
    '''
    reset the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('DEALLOCATE canceled, go back to NOT_READY state')
        return False
    except fysom.Error:
        log.error('DEALLOCATE could not be performed, wrong input state')
        return False
    return True


def abort(master_fsm):
    '''
    abort the master_fsm, handle the exceptions and return status
    :param master_fsm:
    :return:
    '''
    log = logging.getLogger(sys.modules['__main__'].__name__)
    try:
        getattr(master_fsm, sys._getframe().f_code.co_name)()
    except fysom.Canceled:
        log.warning('ABORT canceled, go back to previous state')
        return False
    except fysom.Error:
        log.error('ABORT could not be performed, wrong input state')
        return False
    return True