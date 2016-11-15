from subprocess import Popen, PIPE

class ZFitsWriter:
    def __init__(self):
        self.writer = None
        return

    def start_writing(self):
        self.writer = Popen('/home/sst1m-user/SST1M/digicam-raw/Build.Release/bin/ZFitsWriter --output_dir /data/datasets/ --input tcp://localhost:13581 --loop',
                            env=dict(os.environ, my_env_prop='value'))
        return

    def stop_writing(self):
        self.writer.terminate()
        return