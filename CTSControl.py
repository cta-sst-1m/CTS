import cts.master as cts_master
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
    Welcome in the CTS control.

    here are the functions available from ctsclient:

    - Generic control functions:
        >> ctsmaster.reset()
        >> ctsmaster.update()
        >> ctsmaster.plot()
        >> ctsmaster.print_status()

    - Low level LED control:
        >> ctsmaster.turn_on( pixel , led_type , level )
        >> ctsmaster.turn_off( pixel , led_type )
        >> ctsmaster.all_on( led_type , level )

    - Predefined scans:
        >> ctsmaster.loop_over_dc_pixels( level , timeout )
        >> ctsmaster.loop_over_ac_pixels( level , timeout )
        >> ctsmaster.loop_over_dc_patches( level , timeout )
        >> ctsmaster.loop_over_ac_patches( level , timeout )

    For more informations on the argument of each function, type:

        >> help(ctsmaster.function_you_want_to_understand)

    From ctsmaster, you have access to all mapping information through the CTS class accessible
    with ctsmaster.cts
    '''
    print(string_help)


if __name__ == "__main__":
    ion()
    ctsmaster = cts_master.CTSMaster(float(sys.argv[1]))

    print('---|> The client is starting, reset of the board can take a little time')
    ctsmaster.reset()
    cts = ctsmaster.cts
    generator = ctsmaster.generator
    print('---|> The client have been started')
    man()
    try:
        IPython.embed()
    finally:
        print('---|> The client will be reset and turned off, wait...')
        ctsmaster.reset()
        ctsmaster.cts_client.client_off()
        ctsmaster.generator.inst.write('LOCAL')
        ctsmaster.generator.inst.close()
        print('---|> Done')
