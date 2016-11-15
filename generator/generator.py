import visa,time



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
    def __init__(self,url = "129.194.55.68", rm = visa.ResourceManager('@py')):
        self.rm = rm
        self.inst = self.rm.open_resource("TCPIP::"+url+"::9221::SOCKET")
        return

    def __del__(self):
        self.inst.write('LOCAL')
        self.inst.close()

    def start_trigger(self):
        if self.conf_type == 'continuous': self.inst.write('OUTPUT ON')
        elif self.conf_type == 'burst': self.inst.write('*TRG')
        return

    def stop_trigger(self):
        if self.conf_type == 'continuous' or self.conf_type== 'burst': self.inst.write('OUTPUT OFF')
        return

    def configure_trigger(self,n_trigger):
        self.inst.write('BSTCOUNT '+str(n_trigger))
        return

    def load_configuration(self,conf_type):
        if conf_type=='continuous':
            self.inst.write('WAVE SQUARE')
            self.inst.write('FREQ 1')
            self.inst.write('AMPL 0.8')
            self.inst.write('DCOFFS -0.4')
            self.inst.write('ZLOAD 50')

        elif conf_type=='burst':
            self.inst.write('WAVE PULSE')
            self.inst.write('OUTPUT INVERT')
            self.inst.write('ZLOAD 50')
            self.inst.write('AMPL 0.8')
            self.inst.write('DCOFFS -0.4')
            self.inst.write('PULSSYMM 50')
            self.inst.write('PULSFREQ 1000')
            self.inst.write('PULSEDGE 0.000000005')
            self.inst.write('BST NCYC')
            self.inst.write('BSTCOUNT 10')
            self.inst.write('BSTTRGSRC MAN')
            self.inst.write('OUTPUT ON')

            #self.inst.write('TRGOUT BURST')
        self.conf_type = conf_type

        return




if __name__ == "__main__":
    generator =  Generator()
    try:
        generator.load_configuration(conf_type='burst')
        embed()
    finally:
        generator.inst.write('LOCAL')
        generator.inst.close()
