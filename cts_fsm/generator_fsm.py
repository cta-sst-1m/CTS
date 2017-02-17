import utils.fsm_def
from fysom import Fysom
import generator.generator as generator
import logging,sys

try:
    import IPython
except ImportError:
    import code

class GeneratorFsm(Fysom,generator.Generator):
    """
    CTSMaster implements the FSM which control the experimental setup

    """
    def __init__(self, fsm_table=utils.fsm_def.FSM_TABLE, options = None,
                 logger_name=sys.modules['__main__'].__name__ ):
        """
        Initialise function of the generator FSM

        :param fsm_table: Table defining the FSM
        :param options  : A dictionary containing the necessary options
        :param : logger_name : the parent logger name
        :param fsm_table: Table defining the FSM
        """

        callbacks = {'onbeforeallocate': self.onbeforeallocate,
                     'onnot_ready': self.onnot_ready,
                     'onbeforeconfigure': self.onbeforeconfigure,
                     'onstand_by': self.onstand_by,
                     'onbeforestart_run': self.onbeforestart_run,
                     'onready': self.onready,
                     'onbeforestart_trigger': self.onbeforestart_trigger,
                     'onrunning': self.onrunning,
                     'onbeforestop_trigger': self.onbeforestop_trigger,
                     'onbeforestop_run': self.onbeforestop_run,
                     'onbeforereset': self.onbeforereset,
                     'onbeforedeallocate': self.onbeforedeallocate}

        Fysom.__init__(self, cfg = fsm_table, callbacks = callbacks)

        # Set up the logger
        self.logger = logging.getLogger(logger_name + '.cts_fsm')
        self.logger.info('\t-|--|> Append the GeneratorFSM to the setup')
        self.options = options
    # Actions callbacks


    def onbeforeallocate(self, e):
        """
        FSM callback on the allocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            generator.Generator.__init__(self,logger_name=sys.modules['__main__'].__name__ ,
                                         url = self.options['generator_url'],
                                         slave_url= self.options['slave_generator_url'] if 'slave_generator_url' in self.options.keys() else None )
            self.logger.debug('\t-|--|> Generator %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('\t-|--|> Failed allocation of Generator %s: ', inst)
            return False



    def onbeforeconfigure(self, e):
        """
        FSM callback on the configure event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.debug('-|--|>  Configure the Generator with: ')
            for k,v in self.options.items():
                self.logger.debug('\t-|--|--|>  %s :\t %s '%(k,v))
            try:
                self.apply_config(self.options['configuration_mode'])
                if ('rate' in self.options.keys()) and ('number_of_pulses' in self.options.keys()):
                    self.configure_trigger( freq=int(self.options['rate']), n_pulse=int(self.options['number_of_pulses']))
                if 'slave_generator_url' in self.options.keys():
                    self.configure_slave(amplitude=self.options['slave_amplitude'] if 'slave_amplitude' in self.options.keys() else 0.,
                                         offset=self.options['slave_offset'] if 'slave_offset' in self.options.keys() else 0.)
            except Exception as inst:
                raise inst
            self.logger.debug('-|--|> Generator %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('-|--|> Failed configuration of Generator %s: ', inst)
            return False

    def onbeforestart_run(self, e):
        """
        FSM callback on the start_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        return True

    def onbeforestart_trigger(self, e):
        """
        FSM callback on the start_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.debug('-|--|>  Send trigger from Generator ')
            try:
                #print('No trig')
                self.start_trigger_sequence()
            except Exception as inst:
                raise inst
            self.logger.debug('-|--|> Generator %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('-|--|> Failed configuration of Generator %s: ', inst)
            return False
        return True

    def onbeforestop_trigger(self, e):
        """
        FSM callback on the stop_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            self.logger.debug('-|--|>  Send trigger from Generator ')
            try:
                #print('No stop trig')
                self.stop_trigger_sequence()
            except Exception as inst:
                raise inst
            self.logger.debug('-|--|> Generator %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('-|--|> Failed configuration of Generator %s: ', inst)
            return False
        return True

    def onbeforestop_run(self, e):
        """
        FSM callback on the stop_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        return True

    def onbeforereset(self, e):
        """
        FSM callback on the reset event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.debug('-|--|>  Reset the Generator with: ')
            try:
                self.reset_generator()
            except Exception as inst:
                raise inst
            self.logger.debug('-|--|> Generator %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('-|--|> Failed Reset of Generator %s: ', inst)
            return False

    def onbeforedeallocate(self, e):
        """
        FSM callback on the deallocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.debug('-|--|>  Deallocate the Generator with: ')
            try:
                self.close_generator()
            except Exception as inst:
                raise inst
            self.logger.debug('-|--|> Generator %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('-|--|> Failed Deallocate of Generator %s: ', inst)
            return False

    def onbeforeabort(self, e):
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
        self.logger.debug('-|--|>Generator is in NOT_READY state')
        return True

    def onready(self, e):
        """
        FSM callback when reaching the ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('-|--|> Generator is in READY state')
        return True

    def onstand_by(self, e):
        """
        FSM callback when reaching the stand_by state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('-|--|> Generator is in STAND_BY state')
        return True

    def onrunning(self, e):
        """
        FSM callback when reaching the running state

        :param e: event instance(see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('-|--|> Generator is in RUNNING state')
        return True
