import mts.master as mts_master
import sys
from matplotlib.pyplot import ion

try:
    import IPython
except ImportError:
    import code


    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()
        ion()

def man():
    string_help = '''
    Welcome in the MTS control.

    here are the functions available from ctsclient:

    - Generic control fun
    TODO
    '''
    print(string_help)


if __name__ == "__main__":
    ion()
    mtsmaster = mts_master.MTSMaster()
    genmaster = mtsmaster.generatorMaster
    genslave = mtsmaster.generatorSlave
    man()
    try:
        IPython.embed()
        # Start with dark run
        # mtsmaster.dark_run()
        # mtsmaster.low_run()
        # mtsmaster.medium_run()
        # mtsmaster.high_run()
    finally:
        mtsmaster.generatorMaster.inst.write('LOCAL')
        mtsmaster.generatorMaster.inst.close()
        mtsmaster.generatorSlave.inst.write('LOCAL')
        mtsmaster.generatorSlave.inst.close()
        print('---|> Done')
