from subprocess import Popen, PIPE
import time


class CameraServer:
    '''
    Wrapper around the CameraServer
    '''

    def __init__(self):
        self.cam_server = None
        return

    def configuration(self):

    def start_cam_server(self):
        self.cam_server = Popen(
            '/home/sst1m-user/SST1M/digicam-raw/Build.Release/bin/ZFitsWriter --output_dir /data/datasets/ --input tcp://localhost:13581 --loop',
            env=dict(os.environ, my_env_prop='value'))
        return

    def stop_cam_server(self):
        self.cam_server.terminate()
        self.cam_server.kill()
        return