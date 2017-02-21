import fysom,logging,sys,time

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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'not_ready'
        if i>99:
            log.warning('ALLOCATE timeout, go back to UNALLOCATED state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'ready'
        if i>99:
            log.warning('CONFIGURE timeout, go back to NOT_READY state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'stand_by'
        if i>99:
            log.warning('START_RUN timeout, go back to READY state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'running'
        if i>99:
            log.warning('START_TRIGGER timeout, go back to STAND_BY state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'stand_by'
        if i>99:
            log.warning('STOP_TRIGGER timeout, go back to RUNNING state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'ready'
        if i>99:
            log.warning('STOP_RUN timeout, go back to STAND_BY state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'not_ready'
        if i>99:
            log.warning('RESET timeout, go back to READY state')
            return False
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
        i,is_ready = 0,False
        while i<100 and not is_ready:
            i+=1
            time.sleep(0.1)
            is_ready = master_fsm.current == 'unallocated'
        if i>99:
            log.warning('DEALLOCATE timeout, go back to RESET state')
            return False
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