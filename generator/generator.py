import visa, time,logging

try:
    from IPython import embed
except ImportError:
    import code


    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


class Generator:
    def __init__(self,logger_name ,url = "129.194.52.244", slave_url = None):
        self.log = logging.getLogger(logger_name+'.generator')
        self.url = url
        if slave_url:
            self.slave_url = slave_url
        try:
            self.rm = visa.ResourceManager('@py')
        except Exception as inst:
            raise inst
        try:
            self.inst = self.rm.open_resource("TCPIP::" + self.url + "::9221::SOCKET")
            if hasattr(self, 'slave_url'):
                self.inst_slave = self.rm.open_resource("TCPIP::" + self.slave_url + "::9221::SOCKET")

        except Exception as inst:
            raise inst
        return

    def apply_config(self, conf_type = 'burst'):
        '''
        configure , method to configure the pulse generator. If n_pulse > 1048575 turn to continuous mode
        :return:
        '''
        self.conf_type = conf_type

        if  self.conf_type == 'continuous' and not hasattr(self,'slave_url'):
            self.inst.write('WAVE PULSE')
            self.inst.write('OUTPUT INVERT')
            self.inst.write('ZLOAD 50')
            self.inst.write('AMPL 0.8')
            self.inst.write('DCOFFS -0.4')
            self.inst.write('PULSWID 0.00000002')
            self.inst.write('PULSFREQ 1000')
            self.inst.write('PULSEDGE 0.000000005')
            self.inst.write('OUTPUT ON')
            self.inst.write('BST INFINITE')
            self.inst.write('BSTTRGSRC MAN')

        elif self.conf_type == 'burst' and not hasattr(self,'slave_url'):
            self.inst.write('WAVE PULSE')
            self.inst.write('OUTPUT INVERT')
            self.inst.write('ZLOAD 50')
            self.inst.write('AMPL 0.8')
            self.inst.write('DCOFFS -0.4')
            self.inst.write('PULSWID 0.00000002')
            self.inst.write('PULSFREQ 1000')
            self.inst.write('PULSEDGE 0.000000005')
            self.inst.write('OUTPUT ON')
            self.inst.write('BST NCYC')
            self.inst.write('BSTCOUNT 1')
            self.inst.write('BSTTRGSRC MAN')

        elif  hasattr(self,'slave_url'):
            print('todo')
        return

    def configure_trigger(self, freq = 1000 , n_pulse = 10 ):
        if self.conf_type == 'continuous':
            self.inst.write('PULSFREQ '+str(freq))
        elif self.conf_type == 'burst':
            self.inst.write('BSTCOUNT '+str(n_pulse))
            self.inst.write('PULSFREQ '+str(freq))
        return

    def configure_slave(self, amplitude = 0 , offset = 0 ):
        self.inst_slave.write('AMPL %0.3f'%amplitude)
        self.inst_slave.write('DCOFFS %0.4f'%offset)
        return

    def start_trigger_sequence(self):
        '''

        :return:
        '''
        self.inst.write('*TRG')
        return


    def stop_trigger_sequence(self):
        if self.conf_type == 'continuous': self.inst.write('*TRG')
        return

    def reset_generator(self):
        self.inst.write('*RST')
        return


    def close_generator(self):
        '''

        :return:
        '''
        self.inst.write('LOCAL')
        self.inst.close()
        self.rm.close()
        return
