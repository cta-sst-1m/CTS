#!/usr/bin/env python3

# external modules
from optparse import OptionParser
from  yaml import load,dump,load_all
import matplotlib.pyplot as plt
import logging,sys
from cts_fsm.master_fsm import MasterFsm
import time,os
#internal modules
from utils import logger


if __name__ == '__main__':
    """
    The main call

    """
    parser = OptionParser()

    # Job configuration (the only mandatory option)
    parser.add_option("-y", "--yaml_config", dest="yaml_config",
                      help="full path of the yaml configuration function",
                      default='/data/software/CTS/options/hv_off.yaml')

    # Other options allows to overwrite the yaml_config interactively

    # Output level
    parser.add_option("-v", "--verbose",
                      action="store_false", dest="verbose", default=True,
                      help="move to debug")

    # Steering of the passes
    parser.add_option("-o", "--output_directory", dest="output_directory",
                      help="Where to store the data from this run", default=None)

    # Steering of the passes
    parser.add_option("-b", "--output_directory_basis", dest="output_directory_basis",
                      help="Basis directory for commissioning data storage", default='/data/datasets/DigiCamCommissionning')


    # Parse the options
    (options, args) = parser.parse_args()

    # Load the YAML configuration
    options_yaml = {}
    with open(options.yaml_config) as f:
        for data in load_all(f):
            options_yaml[data['type']]={}
            for k,v in data.items():
                if k == 'type': continue
                options_yaml[data['type']][k]=v

    # Update with interactive options
    for key,val in options_yaml['steering'].items():
        if not (key in options.__dict__.keys()):
            options.__dict__[key]=val
        else:
            options_yaml['steering'][key]=options.__dict__[key]

    __name__ = options_yaml['steering']['name']

    # Check if the directory name was specified, otherwise replace by the steering name
    if not options_yaml['steering']['output_directory']:
        print('\t\t-|> No output_directory option was specified, will use the steering name: %s'
                         % options_yaml['steering']['name'])
        options_yaml['steering']['output_directory'] = options_yaml['steering']['name']

    _tmp_dir = time.strftime(options_yaml['steering']['output_directory_basis'] + '/%Y%m%d', time.gmtime())

    # If no directory exists for today, then create it
    if not os.path.isdir(_tmp_dir):
        os.mkdir(_tmp_dir)

    options_yaml['steering']['output_directory'] = _tmp_dir + '/' + options_yaml['steering']['output_directory']
    # Create the new directory. If it exist, increment
    if not os.path.isdir(options_yaml['steering']['output_directory']):
        os.mkdir(options_yaml['steering']['output_directory'])
    else:
        list_dir = os.listdir(os.path.dirname(options_yaml['steering']['output_directory']))
        n_dir = 0
        for d in list_dir:
            if d.count(os.basename(options_yaml['steering']['output_directory']) > 0.5): n_dir += 1
        options_yaml['steering']['output_directory'] += '_%d' % n_dir
        os.mkdir(options_yaml['steering']['output_directory'])

    print('\t\t-|> Will store files in: %s' % options_yaml['steering']['output_directory'])

    # Start the loggers
    logger.initialise_logger( options, )
    # load the analysis module
    analysis_module = __import__('analysis.%s'%options.analysis_module,
                                 locals=None,
                                 globals=None,
                                 fromlist=[None],
                                 level=0)

    # Some logging
    log = logging.getLogger(sys.modules['__main__'].__name__)
    log.info('\t\t-|> Will run %s with the following configuration:'%options_yaml['steering']['name'])
    for key,val in options_yaml.items():
        log.info('\t\t |--|> %s :'%(key))
        for key_sub,val_sub in val.items():
            log.info('\t\t |----|> %s : \t %s'%(key_sub,val_sub))
    log.info('-|')
    
    


    # Start the master FSM
    masterfsm = MasterFsm(logger_name=sys.modules['__main__'].__name__)

    masterfsm.allocate()
    masterfsm.configure()
    masterfsm.start_run()
    masterfsm.start_trigger()
    masterfsm.stop_trigger()
    masterfsm.stop_run()
    masterfsm.reset()
    masterfsm.deallocate()




