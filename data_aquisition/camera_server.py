from subprocess import Popen, PIPE
import time


class CameraServer:
    '''
    Wrapper around the CameraServer
    '''

    def __init__(self):
        self.cam_server = None
        self.logger = logger.initialise_logger( logname=sys.modules['__main__'].__name__+'', verbose = options_yaml['steering']['verbose'],
                              logfile = '%s/%s_cameraserver.log'%(options_yaml['steering']['output_directory'],
                                                     options_yaml['steering']['name']))
        return

    def configuration(self,config):
        """
        Config is a dictionnary whose key correspond to the private members of the ZFitsWriter
        :param config:
        :return:
        """
        for key , val in config.items():
            if hasattr(self,key):
                setattr(self,key,val)


    def start_cam_server(self):
        self.cam_server = Popen(
            'sudo /home/sst1m-user/SST1M/digicam-raw/Build.Release/bin/digicam_server --output_dir /data/datasets/ --input tcp://localhost:13581 --loop',
            env=dict(os.environ, my_env_prop='value'))
        return

    def stop_cam_server(self):
        self.cam_server.terminate()
        self.cam_server.kill()
        return

    '''sudo Build.Release/bin/digicam_server -t 1 -s -A 1 -L eth2
    -b 0 -M1-9
    -N0,1,2,3,4,5,6,7,8,9,20,21,22,23,24,25,26,27,28,29,10,11,12,13,14,15,16,17,18,19 -T -1 -x /data/software/DAQ/CamerasToACTL/Cameras/Digicam/digicam_pixels_mapping_V3.txt
     -F 3000 -i 1000000 -I 500000 -q 300000 -u 10000000000'''