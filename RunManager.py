#!/usr/bin/env python3

# external modules
from optparse import OptionParser
from  yaml import load, dump, load_all
import logging, sys
from setup_fsm.master_fsm import MasterFsm
import time, os
import fysom
# internal modules
from utils import logger

try:
    import IPython
except ImportError:
    import code


def load_configuration(options):
    """
    Merge the interactive options with the yaml options to configure the data taking
    :param options:
    :return:
    """

    # Load the YAML configuration
    options_yaml = {}
    with open(options.yaml_config) as f:
        for data in load_all(f):
            options_yaml[data['type']] = {}
            for k, v in data.items():
                if k == 'type': continue
                options_yaml[data['type']][k] = v

    # Update with interactive options
    for key, val in options.__dict__.items():
        if not (key in options_yaml['steering'].keys()):
            options_yaml['steering'][key] = val
        else:
            options_yaml['steering'][key] = val

    return options_yaml


def create_directory(options):
    """
    Create the output directory containing the logs and output file from the writer
    :param options:
    :return:
    """

    # Check if the directory name was specified, otherwise replace by the steering name
    if not options['steering']['output_directory']:
        options['steering']['output_directory'] = options['steering']['name']

    _tmp_dir = time.strftime(options['steering']['output_directory_basis'] + '/%Y%m%d', time.gmtime())

    # If no directory exists for today, then create it
    if not os.path.isdir(_tmp_dir):
        os.mkdir(_tmp_dir)

    options['steering']['output_directory'] = _tmp_dir + '/' + options['steering']['output_directory']
    # Create the new directory. If it exist, increment
    if not os.path.isdir(options['steering']['output_directory']):
        os.mkdir(options['steering']['output_directory'])
    else:
        list_dir = os.listdir(os.path.dirname(options['steering']['output_directory']))
        n_dir = 0
        for d in list_dir:
            if d.count(os.path.basename(options['steering']['output_directory'])) > 0.5: n_dir += 1
        options['steering']['output_directory'] += '_%d' % n_dir
        os.mkdir(options['steering']['output_directory'])


if __name__ == '__main__':
    """
    The main call

    """
    parser = OptionParser()

    # Job configuration (the only mandatory option)
    parser.add_option("-y", "--yaml_config", dest="yaml_config",
                      help="full path of the yaml configuration function",
                      default='/data/software/CTS/setup_config/scan_ac_led.yaml')

    # Other options allows to overwrite the steering part of the yaml_config interactively

    # Output level
    parser.add_option("-v", "--verbose",
                      action="store_false", dest="verbose", default=True,
                      help="move to debug")

    # Steering of the passes
    parser.add_option("-o", "--output_directory", dest="output_directory",
                      help="Where to store the data from this run")

    # Steering of the passes
    parser.add_option("-b", "--output_directory_basis", dest="output_directory_basis",
                      help="Basis directory for commissioning data storage", default='/data/datasets/TEST')

    # Parse the options
    # Parse the options
    (options, args) = parser.parse_args()
    # Merge the configurations of yaml with the inteactive one
    options = load_configuration(options)
    # Rename the process
    __name__ = 'RunManager'#options['steering']['name']
    # Create the directory
    create_directory(options)
    # Start the loggers
    logger.initialise_logger(logname=sys.modules['__main__'].__name__, verbose=options['steering']['verbose'],
                             logfile='%s/%s.log' % (options['steering']['output_directory'],
                                                    options['steering']['name']))
    # Some logging
    log = logging.getLogger(sys.modules['__main__'].__name__)

    log.info('\t\t-|----------------------------------------------------------------------------')
    log.info('\t\t-|> Run %s protocol' % options['steering']['name'])
    log.info('\t\t-|----------------------------------------------------------------------------')
    log.info('\t\t-|> Main configuration :')
    log.info('\t\t-|--|> output directory: %s' % options['steering']['output_directory'])

    for key, val in options.items():
        log.info('\t\t |--|> %s :' % (key))
        for key_sub, val_sub in val.items():
            log.info('\t\t |----|> %s : \t %s' % (key_sub, val_sub))
    log.info('\t\t-|----------------------------------------------------------------------------')

    log.info('\033[1m\033[91m\t\t-|> Build the experimental setup\033[0m' )

    # Start the master FSM
    masterfsm = MasterFsm(options=options, logger_name=sys.modules['__main__'].__name__)

    # if a protocol has been defined
    if 'protocol_configuration' in options.keys():
        if isinstance(options['protocol_configuration']['name'], list ):
            for protocol_config in options['protocol_configuration']['name']:
                protocol = __import__('setup_protocols.%s' % protocol_config,
                                      locals=None,
                                      globals=None,
                                      fromlist=[None],
                                      level=0)
            if protocol.run(masterfsm):
                log.info('\t\t-|----------------------------------------------------------------------------')
        else:
            protocol = __import__('setup_protocols.%s' % options['protocol_configuration']['name'],
                                  locals=None,
                                  globals=None,
                                  fromlist=[None],
                                  level=0)
            if protocol.run(masterfsm):
                log.info('\t\t-|----------------------------------------------------------------------------')
                log.info('\t\t-|> Ready to analyse')


    else:
        try:
            masterfsm.allocate()
            masterfsm.configure()
            masterfsm.start_run()
            masterfsm.start_trigger()
            time.sleep(30)
            masterfsm.stop_trigger()
            masterfsm.stop_run()
            masterfsm.reset()
            masterfsm.deallocate()
            IPython.embed()

        finally:
            print('\t\t-|> Done')
