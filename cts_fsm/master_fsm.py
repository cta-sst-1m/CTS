import utils.fsm_def
from fysom import Fysom
import generator.generator as generator
import logging,time,os
import cts.master as cts_master
from cts_fsm import cts_fsm,writer_fsm,camera_server_fsm,generator_fsm
import pickle

try:
    import IPython
except ImportError:
    import code

class MasterFsm(Fysom):
    """
    CTSMaster implements the FSM which control the experimental setup

    """

    def __init__(self, fsm_table=utils.fsm_def.FSM_TABLE, options = None , logger_name='master_fsm'):
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
        self.options = options
        self.logger = logging.getLogger(logger_name + '.master_fsm')
        self.logger.info('---|> Start the Master FSM')
        if not os.path.isfile(self.options['steering']['output_directory_basis']+"/run.p"):
            pickle.dump({'run_number': 0},
                        open(self.options['steering']['output_directory_basis'] + '/run.p', "wb"))

        self.run_number = pickle.load( open( self.options['steering']['output_directory_basis']+"/run.p", "rb" ) )['run_number']

        
        # Perform some options manipulation
        
        # Create output directory if it does not exist
        if 'writer_configuration' in self.options:

            # Append the path to the writer if exist

            self.options['writer_configuration']['output_dir'] = self.options['steering']['output_directory']
            self.options['writer_configuration']['comp_scheme'] = self.options['writer_configuration'].pop(
                'compression')
            self.options['writer_configuration']['num_comp_threads'] = self.options['writer_configuration'].pop(
                'number_of_trhead')
            self.options['writer_configuration']['num_comp_threads'] = self.options['writer_configuration'].pop(
                'number_of_trhead')


            # Initialise the components
        if 'cts_configuration' in self.options.keys():
            self.elements['cts'] = cts_fsm.CTSFsm(options = options['cts_configuration'] ,
                                                            logger_name=logger_name + '.master_fsm')

        if 'writer_configuration'  in self.options.keys():
            self.elements['writer'] = writer_fsm.WriterFsm(options=options['writer_configuration'],
                                          logger_name=logger_name + '.master_fsm')

        if 'camera_server_configuration' in self.options.keys():
            self.elements['camera_server'] = camera_server_fsm.CameraServerFsm(options=options['camera_server_configuration'],
                                          logger_name=logger_name + '.master_fsm')

        if 'generator_configuration' in self.options.keys():
            self.elements['generator'] = generator_fsm.GeneratorFsm(options=options['generator_configuration'],
                                          logger_name=logger_name + '.master_fsm')



    # Actions callbacks

    def onallocate(self, e):
        """
        FSM callback on the allocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            for key,val in self.elements.items():
                val.allocate()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key,val in self.elements.items():
                if val.current != 'not_ready':
                    raise Exception('Element %s not in NOT_READY state'%key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed allocation of MasterFSM %s: ', inst.__cause__)
            return False

        # Check if all elements went to the proper status

    def onconfigure(self, e):
        """
        FSM callback on the configure event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            for key, val in self.elements.items():
                val.configure()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'ready':
                    raise Exception('Element %s not in READY state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed configuration of MasterFSM %s: ', inst.__cause__)
            return False


    def onstart_run(self, e):
        """
        FSM callback on the start_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.run_number +=1
        pickle.dump({'run_number':self.run_number}, open(self.options['steering']['output_directory_basis']+'/run.p', "wb"))
        try:
            for key in ['writer','camera_server','cts','generator']:
                self.element.start_run()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'stand_by':
                    raise Exception('Element %s not in STAND_BY state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed start_run of MasterFSM %s: ', inst.__cause__)
            return False

    def onstart_trigger(self, e):
        """
        FSM callback on the start_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            for key in ['cts','generator']:
                if key in self.elements.keys:
                    self.element.start_trigger()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'running':
                    raise Exception('Element %s not in RUNNING state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed start_trigger of MasterFSM %s: ', inst.__cause__)
            return False



    def onstop_trigger(self, e):
        """
        FSM callback on the stop_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            for key in ['cts','generator']:
                if key in self.elements.keys:
                    self.element.stop_trigger()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'stand_by':
                    raise Exception('Element %s not in STANDBY state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed stop_trigger of MasterFSM %s: ', inst.__cause__)
            return False


    def onstop_run(self, e):
        """
        FSM callback on the stop_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            for key in ['generator','cts','camera_server','writer']:
                if key in self.elements.keys:
                    self.element.stop_run()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'ready':
                    raise Exception('Element %s not in READY state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed stop_run of MasterFSM %s: ', inst.__cause__)
            return False

    def onreset(self, e):
        """
        FSM callback on the reset event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            for key, val in self.elements.items():
                val.reset()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'not_ready':
                    raise Exception('Element %s not in NOTREADY state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed reset of MasterFSM %s: ', inst.__cause__)
            return False

    def ondeallocate(self, e):
        """
        FSM callback on the deallocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            for key, val in self.elements.items():
                val.reset()
            self.logger.info('---|>  %s : %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'unallocated':
                    raise Exception('Element %s not in UNALLOCATED state' % key)
            return True

        except Exception as inst:
            self.logger.info('------|> Failed reset of MasterFSM %s: ', inst.__cause__)
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
        for key, val in self.elements.items():
            val.onnot_ready(e)
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

    def onready(self, e):
        """
        FSM callback when reaching the ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        for key, val in self.elements.items():
            val.onready(e)
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

    def onstand_by(self, e):
        """
        FSM callback when reaching the stand_by state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        for key, val in self.elements.items():
            val.onstand_by(e)
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

    def onrunning(self, e):
        """
        FSM callback when reaching the running state

        :param e: event instance(see fysom)
        :return: handler for the fsm (boolean)
        """
        for key, val in self.elements.items():
            val.onrunning(e)
        self.logger.info('---|> %s,%s,%s')%(e.event,e.src,e.dst)
        return True

