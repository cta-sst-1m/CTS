import utils.fsm_def
from fysom import Fysom
from data_aquisition import camera_server
import logging,sys
import inspect

try:
    import IPython
except ImportError:
    import code

class CTSFsm(Fysom,camera_server.CameraServer):
    """
    The FSM that control the ZFitsCameraServer

    """

    def __init__(self, fsm_table=utils.fsm_def.FSM_TABLE, options = None,
                 logger_name=sys.modules['__main__'].__name__ ,
                 logger_dir = '.'):
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
        self.logger = logging.getLogger(logger_name + '.camserver_fsm')
        self.logger.info('\t-|--|> Append the CTSFsm to the setup')
        self.options = options
        self.logger_dir = logger_dir
    # Actions callbacks

    def onbeforeallocate(self, e):
        """
        FSM callback on the allocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            camera_server.CameraServer.__init__(self,log_location = self.logger_dir)
            self.logger.debug('\t-|--|> CameraServer %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('\t-|--|> Failed allocation of CameraServer %s: ', inst.__cause__)
            return False

    def onbeforeconfigure(self, e):
        """
        FSM callback on the configure event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.debug('-|--|>  Configure the CameraServer with: ')
            for k,v in self.options.items():
                self.logger.debug('\t-|--|--|>  %s :\t %s '%(k,v))
            self.configuration(self.options)
            self.logger.debug('-|--|>  Start the CameraServer, see log')
            try:
                self.start_server()
            except Exception as inst:
                self.logger.error(inst)
            self.logger.debug('-|--|> CameraServer %s : move from %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.error('-|--|> Failed configuration and start-up of CameraServer %s: ', inst.__cause__)
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
        return True

    def onbeforestop_trigger(self, e):
        """
        FSM callback on the stop_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
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
            self.stop_server()
            self.logger.info('-|--|> CameraServer have been stopped, see log')
            return True
        except Exception as inst:
            self.logger.error('-|--|>  Failed reseting the camera server %s: ', inst.__cause__)
            return False

    def onbeforedeallocate(self, e):
        """
        FSM callback on the deallocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        return True

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
        self.logger.debug('-|--|>CTSFsm is in NOT_READY state')
        return True

    def onready(self, e):
        """
        FSM callback when reaching the ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('-|--|> CTSFsm is in READY state')
        return True

    def onstand_by(self, e):
        """
        FSM callback when reaching the stand_by state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('-|--|> CTSFsm is in STAND_BY state')
        return True

    def onrunning(self, e):
        """
        FSM callback when reaching the running state

        :param e: event instance(see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('-|--|> CTSFsm is in RUNNING state')
        return True

