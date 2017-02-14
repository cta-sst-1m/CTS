import utils.fsm_def
from fysom import Fysom
import generator.generator as generator
import logging

try:
    import IPython
except ImportError:
    import code

class GeneratorFsm(Fysom):
    """
    CTSMaster implements the FSM which control the experimental setup

    """

    def __init__(self, fsm_table=utils.fsm_def.FSM_TABLE, url='129.194.55.68', logger_name='master'):
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
        self.urlconfig = url
        self.logger = logging.getLogger(logger_name + '.generator')
        self.logger.info('---|> Append the generator to the setup')

        """
        onbeforeallocate (fired before allocate)  can return false
        onleaveunallocated (fired when leaving allocated) can return false
        onenternot_ready (fired when entering not_ready) eq. onnot_ready
        onafterallocate (fired after allocate have been fired)  eq. onallocate
        """

    # Actions callbacks

    def onallocate(self, e):
        """
        FSM callback on the allocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """

        try:
            self.object = generator.Generator.__init__(self, self.urlconfig)  # TODO use the configsŝ
            self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
            return True
        except Exception as inst:
            self.logger.info('------|> Failed allocation of generator %s: ', inst.__cause__)
            return False

    def onconfigure(self, e):
        """
        FSM callback on the configure event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        print('enters2')
        try:
            # TODO check the configs (only allow to move to ready if configurations exists and are applied)
            self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
            print('enters')
            print(self.object.rm.last_status)
            print('bla')
            self.object.apply_config('continuous')
            return True
        except Exception as inst:
            self.logger.info('------|> Failed configuration of generator %s: ', inst.__cause__)
            return False

    def onstart_run(self, e):
        """
        FSM callback on the start_run event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
        return True

    def onstart_trigger(self, e):
        """
        FSM callback on the start_trigger event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
            self.object.start_trigger_sequence()
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
            self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
            self.object.stop_trigger_sequence()
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
        self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
        return True

    def onreset(self, e):
        """
        FSM callback on the reset event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
            self.object.reset_generator()
            return True
        except Exception as inst:
            self.logger.info('------|> Failed reseting the generator %s: ', inst.__cause__)
            return False

    def ondeallocate(self, e):
        """
        FSM callback on the deallocate event

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        try:
            self.logger.info('------|> Generator %s : %s to %s' % (e.event, e.src, e.dst))
            self.object.close_generator()
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
        print(e.event,e.src,e.dst)
        return True

    def onready(self, e):
        """
        FSM callback when reaching the ready state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        print(e.event,e.src,e.dst)
        return True

    def onstand_by(self, e):
        """
        FSM callback when reaching the stand_by state

        :param e: event instance (see fysom)
        :return: handler for the fsm (boolean)
        """
        print(e.event,e.src,e.dst)
        return True

    def onrunning(self, e):
        """
        FSM callback when reaching the running state

        :param e: event instance

if __name__ == "__main__":
    generator =  Generator()
    generator.initialise()
    try:
        generator.apply_config(conf_type='continuous')
        embed()
    finally:
        generator.close()
(see fysom)

        :return: handler for the fsm (boolean)
        """
        print(e.event,e.src,e.dst)
        return True


if __name__ == "__main__":
    fsm_generator = GeneratorFsm()

    logging.basicConfig(filename='example.log', level=logging.DEBUG)

    print('---|> The FSM generator is starting')

    try:
        fsm_generator.allocate()
        fsm_generator.current
        fsm_generator.configure()
        fsm_generator.current
        fsm_generator.start_run()
        fsm_generator.current
        fsm_generator.start_trigger()
        fsm_generator.current

        IPython.embed()
    finally:
        print('---|> Done')
