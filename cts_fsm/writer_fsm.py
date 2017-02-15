import utils.fsm_def
from fysom import Fysom
from data_aquisition import zfits_writer
import logging

try:
    import IPython
except ImportError:
    import code

class GeneratorFsm(Fysom):
    """
    CTSMaster implements the FSM which control the experimental setup

    """

    def __init__(self, fsm_table=utils.fsm_def.FSM_TABLE, options = None, logger_name='writer'):
        """
        Initialise function of the generator FSM

        :param fsm_table: Table defining the FSM
        :param url:       IP address of the generator
        """

        callbacks = {'onbeforeallocate': self.onallocate,
                     'onnot_ready': self.onnot_ready,
                     'onbeforeconfigure': self.onconfigure,
                     'onstand_by': self.onstand_by,
                     'onbeforestart_run': self.onstart_run,
                     'onready': self.onready,
                     'onbeforestart_trigger': self.onstart_trigger,
                     'onrunning': self.onrunning,
                     'onbeforestop_trigger': self.onstop_trigger,
                     'onbeforestop_run': self.onstop_run,
                     'onbeforereset': self.onreset,
                     'onbeforedeallocate': self.ondeallocate}

        Fysom.__init__(self, cfg = fsm_table, callbacks = callbacks)

        # Set up the logger
        self.logger = logging.getLogger(logger_name + '.writer')
        self.logger.info('-----|> Append the writer to the setup')

        self.options = options

    # Actions callbacks

    def onallocate(self, e):
        """
        FSM callback on the allocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.object = zfits_writer.ZFitsWriter.__init__(self)
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed allocation of writer %s: ', inst.__cause__)
            return False

    def onconfigure(self, e):
        """
        FSM callback on the configure event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            self.logger.info('------|> Configure the Writer with: ')
            for k,v in self.options:
                self.logger.info('--------|> %s :\t %s '%(k,v))
            self.object.configuration(self.options)
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed configuration of Writer %s: ', inst.__cause__)
            return False

    def onstart_run(self, e):
        """
        FSM callback on the start_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.object.start_writing()
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed starting the run %s: ', inst.__cause__)
            return False

    def onstart_trigger(self, e):
        """
        FSM callback on the start_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed starting the trigger %s: ', inst.__cause__)
            return False

    def onstop_trigger(self, e):
        """
        FSM callback on the stop_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed stopping the trigger %s: ', inst.__cause__)
            return False

    def onstop_run(self, e):
        """
        FSM callback on the stop_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.object.stop_writing()
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed starting the run %s: ', inst.__cause__)
            return False

    def onreset(self, e):
        """
        FSM callback on the reset event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed reseting the writer %s: ', inst.__cause__)
            return False

    def ondeallocate(self, e):
        """
        FSM callback on the deallocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Writer %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed closing and giving back the hand %s: ', inst.__cause__)
            return False

    def onabort(self, e):
        """
        FSM callback on the abort event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        if self.current == 'running':
            self.stop_trigger(e)
            self.stop_run(e)
            self.reset(e)
        elif self.current == 'stand_by':
            self.stop_run(e)
            self.reset(e)
        elif self.current == 'ready':
            self.reset(e)
        return True

    # States callbacks
    def onnot_ready(self, e):
        """
        FSM callback when reaching the not_ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

    def onready(self, e):
        """
        FSM callback when reaching the ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

    def onstand_by(self, e):
        """
        FSM callback when reaching the stand_by state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

    def onrunning(self, e):
        """
        FSM callback when reaching the running state

        :param e: event instance(see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

