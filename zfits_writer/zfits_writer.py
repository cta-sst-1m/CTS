from subprocess import Popen, PIPE
import time

class ZFitsWriter:
    '''
    Wrapper around the ZFitsWriter

    |------------------------------------------------------------------------------|
    |---------------------------------ZFITS WRITER---------------------------------|
    |-----------------------A compressed FITS writer module------------------------|
    |-It subscribes to streams, sorts out incoming events and writes them to disk--|
    |------------------------------------------------------------------------------|
    Required parameters:
    --output_dir the directory where to write the FITS files
    --input      the zmq input streams config(s)

    Optional arguments, in bytes if applicable:
    --id                the identifier to associate to this writer (for load
                        balancing)
    --max_evts_per_file the number of events to write to a given file before opening
                        a new one. default=100k
     --evts_per_tile     number of events to group and compress at once. default=100
     --num_comp_threads  number of threads to use for compressing data. default=0
     --max_comp_mem      maximum amount of memory to use for compression. default=2GB
     --max_file_size     maximum size of each uncompressed file in MegaBytes. Due to
                         compression, actual files will probably be smaller. default=
                         2GB
     --comp_scheme       which compression scheme to use. default=zrice.
                         available=raw, zlib, fact, diffman16, huffman16,
                         doublediffman16, riceman16, factrice, ricefact, rrice, rice,
                         lzo, zrice, zrice32, lzorice.
    --comp_block_size   size of the the blocks to use for compression. Increase if
                           exception is raised because of blocks too small.
                        default=2880kB
    --head_flush_inter  duration in milliseconds between two flush of the output
                        files header. Default is 10 seconds, 0 disables flushing
    --loop              loops (infinitely) after a run has stopped and continue
                        writing.
    --suffix            add a given suffix in the filename, e.g. a run type

    '''

    def __init__(self):
        self.writer = None
        self.output_dir = time.strftime('/data/datasets/%Y%m%d',time.gmtime())
        self.input = 'tcp://localhost:13581'
        self.loop = ''
        self.max_evts_per_file = 10000
        self.num_comp_threads = 5
        self.comp_scheme = 'zrice'
        self.suffix = ''
        return

    def configuration(self, config):
        """
        Config is a dictionnary whose key correspond to the private members of the ZFitsWriter
        :param config:
        :return:
        """
        for key , val in config.items():
            setattr(self,key,val)


    def start_writing(self):
        list_param = []

        self.writer = Popen('/home/sst1m-user/SST1M/digicam-raw/Build.Release/bin/ZFitsWriter --output_dir /data/datasets/ --input tcp://localhost:13581 --loop',
                            env=dict(os.environ, my_env_prop='value'))
        return

    def stop_writing(self):
        self.writer.terminate()
        self.writer.kill()
        return