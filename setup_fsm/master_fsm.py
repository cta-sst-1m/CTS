import logging
import os
import pickle
import sys

from fysom import Fysom

import utils.fsm_def
from setup_fsm import cts_fsm,writer_fsm,camera_server_fsm,generator_fsm

try:
    import IPython
except ImportError:
    import code

class MasterFsm(Fysom):
    """
    CTSMaster implements the FSM which control the experimental setup

    """

    def __init__(self, fsm_table=utils.fsm_def.FSM_TABLE, options = None , logger_name=sys.modules['__main__'].__name__ ):
        """
        Initialise function of the generator FSM

        :param fsm_table: Table defining the FSM
        :param url:       IP address of the generator
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
        self.options = options
        self.logger = logging.getLogger(logger_name + '.master_fsm')
        self.logger.info('\t-|> Start the Master FSM')
        if not os.path.isfile(self.options['steering']['output_directory_basis']+"/run.p"):
            pickle.dump({'run_number': 0},
                        open(self.options['steering']['output_directory_basis'] + '/run.p', "wb"))

        self.run_number = pickle.load( open( self.options['steering']['output_directory_basis']+"/run.p", "rb" ) )['run_number']
        self.elements = {}
        # Initialise the setup_components
        if 'writer_configuration' in self.options.keys():
            # Append the path to the writer
            self.options['writer_configuration']['output_dir'] = self.options['steering']['output_directory']
            # Update few other parameters
            self.options['writer_configuration']['suffix'] = 'run_%d'%self.run_number
            if 'compression' in self.options['writer_configuration'].keys():
                self.options['writer_configuration']['comp_scheme'] = self.options['writer_configuration'].pop('compression')
            if 'number_of_thread' in self.options['writer_configuration'].keys():
                self.options['writer_configuration']['num_comp_threads'] = self.options['writer_configuration'].pop('number_of_thread')
            if 'number_of_events_per_file' in self.options['writer_configuration'].keys():
                self.options['writer_configuration']['max_evts_per_file'] = self.options['writer_configuration'].pop('number_of_events_per_file')
            # Initialise the componant

            self.logger.debug('\t |--|> Update the writer configuration')
            for k,v in options['writer_configuration'].items():
                self.logger.debug('\t |--|--|> %s : %s'%(k,v))
            self.elements['writer'] = writer_fsm.WriterFsm(options=options['writer_configuration'],
                                          logger_name=logger_name,logger_dir=self.options['steering']['output_directory'] )

        # Initialise the setup_components
        if 'cts_configuration' in self.options.keys():
            self.elements['cts_core'] = cts_fsm.CTSFsm(options = options['cts_configuration'] ,
                                                            logger_name=logger_name )

        if 'camera_server_configuration' in self.options.keys():
            # Build the fadc board mapping and the internal remapping
            options['camera_server_configuration']['M']= ''
            options['camera_server_configuration']['N']= ''
            opt ,optN= '',''
            for c,fadcs in enumerate( options['camera_configuration']['fadcs']):
                for fadc in fadcs:
                    options['camera_server_configuration']['N'] +=optN + '%d'%(c*10+fadc)
                    optN = ','
                    if fadc%10 == 0 : continue
                    options['camera_server_configuration']['M'] +=opt + '%d'%(c*10+fadc)
                    opt =','
            for c in range(3):
                for fadc in range(10):
                    if (str(c*10+fadc) in options['camera_server_configuration']['N'].split(',')): continue
                    options['camera_server_configuration']['N'] += optN + '%d' % (c * 10 + fadc)

            # now reformat M
            i = 0
            start_cnt = 0
            end_cnt = -1
            list_b = [int(b) for b in options['camera_server_configuration']['M'].split(',')]
            lists_consecutive_board=[]
            while i < len(list_b):
                if i == 0 : lists_consecutive_board.append([list_b[i]])
                elif list_b[i] != list_b[i-1]+1:
                    lists_consecutive_board.append([])
                    lists_consecutive_board[-1].append(list_b[i])
                    start_cnt=list_b[i-1]
                elif list_b[i] == list_b[i-1]+1 :
                    lists_consecutive_board[-1].append(list_b[i])
                i+=1
            options['camera_server_configuration']['M'] = ''
            opt = ''
            for list_bs in lists_consecutive_board:
                if list_bs[0]==list_bs[-1]:
                    options['camera_server_configuration']['M']+= opt+'%d'%(list_bs[0])
                else:
                    options['camera_server_configuration']['M']+=opt+'%d-%d'%(list_bs[0],list_bs[-1])
                opt = ','

            self.elements['camera_server'] = camera_server_fsm.CameraServerFsm(options=options['camera_server_configuration'],
                                          logger_name=logger_name,logger_dir=self.options['steering']['output_directory'])



        if 'generator_configuration' in self.options.keys():
            self.elements['generator'] = generator_fsm.GeneratorFsm(options=options['generator_configuration'],
                                          logger_name=logger_name )


    # Actions callbacks

    def onbeforeallocate(self, e):
        """
        FSM callback on the allocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> Start MasterFSM Allocation')
        try:
            status_ok = True
            for key,val in self.elements.items():
                val.allocate()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key,val in self.elements.items():
                if val.current != 'not_ready':
                    raise Exception('Element %s not in NOT_READY state'%key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed ALLOCATE of MasterFSM %s: ', inst.__cause__)
            # revert the child processes
            for key,val in self.elements.items():
                if val.current == 'not_ready':
                    val.deallocate()
            return False

        # Check if all elements went to the proper status

    def onbeforeconfigure(self, e):
        """
        FSM callback on the configure event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> Start MasterFSM Configuration')
        try:
            for key, val in self.elements.items():
                val.configure()
            self.logger.debug('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'ready':
                    raise Exception('Element %s not in READY state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed CONFIGURE of MasterFSM %s: ', inst.__cause__)
            return False


    def onbeforestart_run(self, e):
        """
        FSM callback on the start_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM start-run call')
        self.run_number +=1
        pickle.dump({'run_number':self.run_number}, open(self.options['steering']['output_directory_basis']+'/run.p', "wb"))
        try:
            for key in ['writer','camera_server','cts_core','generator']:
                if key in self.elements.keys():
                    self.elements[key].start_run()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'stand_by':
                    raise Exception('Element %s not in STAND_BY state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed START_RUN of MasterFSM %s: ', inst.__cause__)
            return False

    def onbeforestart_trigger(self, e):
        """
        FSM callback on the start_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        self.logger.debug('\t-|> MasterFSM start-trigger call')
        self.run_number +=1
        pickle.dump({'run_number':self.run_number}, open(self.options['steering']['output_directory_basis']+'/run.p', "wb"))
        try:
            for key in ['cts_core','generator','writer','camera_server']:
                if key in self.elements.keys():
                    self.elements[key].start_trigger()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'running':
                    raise Exception('Element %s not in RUNNING state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed START_TRIGGER of MasterFSM %s: ', inst.__cause__)
            return False



    def onbeforestop_trigger(self, e):
        """
        FSM callback on the stop_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM stop-trigger call')
        try:
            for key in ['generator','cts_core','writer','camera_server']:
                if key in self.elements.keys():
                    self.elements[key].stop_trigger()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'stand_by':
                    raise Exception('Element %s not in STAND_BY state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed STOP_TRIGGER of MasterFSM %s: ', inst.__cause__)
            return False

    def onbeforestop_run(self, e):
        """
        FSM callback on the stop_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM stop-run call')
        try:
            for key in ['camera_server','writer','generator','cts_core']:
                if key in self.elements.keys():
                    self.elements[key].stop_run()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'ready':
                    raise Exception('Element %s not in READY state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed STOP_RUN of MasterFSM %s: ', inst.__cause__)
            return False


    def onbeforereset(self, e):
        """
        FSM callback on the reset event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM reset call')
        try:
            for key in ['writer','camera_server','generator','cts_core']:
                if key in self.elements.keys():
                    self.elements[key].reset()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'not_ready':
                    raise Exception('Element %s not in NOT_READY state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed RESET of MasterFSM %s: ', inst.__cause__)
            return False


    def onbeforedeallocate(self, e):
        """
        FSM callback on the deallocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM deallocate call')
        try:
            for key in self.elements.keys():
                if key in self.elements.keys():
                    self.elements[key].deallocate()
            self.logger.info('\t-|>  Master %s : move from %s to %s' % (e.event, e.src, e.dst))

            for key, val in self.elements.items():
                if val.current != 'unallocated':
                    raise Exception('Element %s not in UNALLOCATTED state' % key)
            return True

        except Exception as inst:
            self.logger.info('\t-|> Failed DEALLOCATE of MasterFSM %s: ', inst.__cause__)
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
        self.logger.debug('\t-|> MasterFSM is in NOT_READY state')
        return True

    def onready(self, e):
        """
        FSM callback when reaching the ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM is in READY state')
        return True

    def onstand_by(self, e):
        """
        FSM callback when reaching the stand_by state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM is on STAND_BY state')
        return True

    def onrunning(self, e):
        """
        FSM callback when reaching the running state

        :param e: event instance(see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.debug('\t-|> MasterFSM is on RUNNING state')
        return True

