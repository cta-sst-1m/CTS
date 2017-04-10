
from subprocess import Popen, PIPE, STDOUT
import time,os,sys
from utils import logger
import logging
from threading import Thread,Event
from queue import Queue, Empty

class CameraServer:
    '''
        Wrapper around the CameraServer

        Available options :
    	-a ip4address     (connect to SWAT server (server mode) or CSP server (client mode) at this IP address - def. localhost)
    	-A int            (do not connect to SWAT, instead treat each n-th event as array event and send it to DAQ)
    	-b port           (listen for data from Digicam at this UDP port - default is 13580. If 0 and -L ==> read all UDP packets)
    	-B int            (timebin size in microsec - default is 1000)
    	-c                (set client mode - that is emulate DIGICAM, and generate/send UDP packets)
    	-d int            (CLIENT MODE: generate this many events - default is 1000)
    	-D                (debug mode, enables some extra messages)
    	-e float          (set period of status reporting - default is 1.000 sec)
    	-F int            (future time margin in timebins - default is 600)
    	-i int            (allocate arena for how many UDP packets - default is 500000)
    	-I int            (set ingest queue depth in items - default is 50000)
    	-j float          (set max localclk jitter - default is 1.000 sec)
    	-l                (liberal mode: accept partial triggers - default is drop any partial triggers)
    	-L iface_str      (use libpcap for UDP packet reception at this interface - root only)
    	-m int            (set size for UDP packets - default is 1500 - CLIENT mode only)
    	-M modules_str    (require/enable those modules (default: 1-9,11-19,21-29, note:0,10,20 are trigger cards) : DD,DD,DD-DD ...)
    	-n int            (CLIENT MODE: number of samples per pixel - default is 25)
    	-N remap_mod_str  (remap idmod - must specify exactly 30 comma separated ints (default: 0,1,2,3,4,5,6....29)
    	-o 0/1            (tell SWAT server that my camera triggers are always sorted w.r.t time - default is 1)
    	-p port           (connect to SWAT server (server mode) or CSP server (client mode) at this port number - default is 13579)
    	-P int            (past time margin in timebins - default is 400)
    	-q int            (set inque depth in items - default is 30000)
    	-r int            (CLIENT MODE: average event rate in camera events/s - poissonian distribution - default is 1000)
    	-R 0/1            (request recv data channel from SWAT server - default is 1)
    	-s                (set server mode)
    	-S 0/1            (request send data channel from SWAT server - default is 1)
    	-t int            (set telescope/client identifier, integer 0 - 99)
    	-T float          (set localclk rate faster/slower than realtime - default is -1.0 ;; neg.val forces decoding as secs + 1/4nsec)
    	-u int            (set socket buffer size - default is 1000000000)
    	-U int            (set bunch queue depth in items - default is 100000)
    	-x fname_str      (read pixel mapping from this file - default is linear pixel mapping)
    	-z port           (start ZMQ socket at this TCP port - default is 13581)
    	-2                (PERFMODE(2): measure performance/bottlenecks: drop packets immediately after ingest)
    	-3                (PERFMODE(3): measure performance/bottlenecks: ingest + merge/sort phase, then drop packet)
    	-4                (PERFMODE(4): measure performance/bottlenecks: ingest + merge/sort + detect array, then drop)
    '''

    def __init__(self, log_location):
        self.camera_server = None
        # self.t telescope ID
        self.t = 1
        # self.s set server mode if true
        self.s = True
        # self.A do not connect SWAT if true
        self.A = 1
        # self.L interface
        self.L = 'eth2'
        # self.b port (if 0 and -L read all UDP packets)
        self.b = 0
        # self.M fadc card
        self.M = None
        # self.N remap id mod
        self.N = None
        # self.T local clock rate
        self.T = -1
        # self.x pixel mapping
        self.x = '/data/software/DAQ/CamerasToACTL/Cameras/Digicam/digicam_pixels_mapping_V3.txt'
        # self.F future time margin ???
        self.F = 3000
        # self.i allocate arena???
        self.i = 1000000
        # self.q  inque depth in items???
        self.q = 300000
        # self.u set socket buffer size
        self.u = 10000000000
        # self.I set socket buffer size
        self.I = 500000

        logger.initialise_logger(logname='CameraServer',
                                 logfile='%s/%s.log' % (log_location, 'cameraserver'), stream=False)
        self.log = logging.getLogger('CameraServer')
        self.log_thread = None
        self.log_queue = None
        self.stop_event = None

    def configuration(self, config):
        """
        Config is a dictionnary whose key correspond to the private members of the ZFitsWriter
        :param config:
        :return:
        """
        for key, val in config.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def enqueue_output(self, q,out,stop_event):
        while not stop_event.is_set():
            for line in iter(out.readline,b''):
                self.log.info('%s', line)
                v = '%r' % (line)
                if v.count('std::runtime_error') > 0:
                    try:
                        raise Exception('CameraServer', line)
                    except Exception:
                        q.put(sys.exc_info())
                #if 'what():  The ZMQ context associated with the specified socket was terminated' in v:
                # raise Exception('')
                q.put(None)


    def start_server(self):
        list_param = []
        for k, v in self.__dict__.items():
            if type(v).__name__ in ['function', 'Logger', 'dict', 'None']: continue
            if k in ['camera_server', 'log', 'current', '_final', 'log_thread', 'log_queue', 'stop_event','logger_dir']: continue
            if type(v).__name__ == 'bool' and v:
                list_param += ['-%s' % k]
            elif k in ['N','M']:
                list_param += ['-%s%s' % (k, str(getattr(self, k)))]
            else:
                list_param += ['-%s' % k, str(getattr(self, k))]
        list_param = ['sudo', '/tmp/jb/v2-trunk/trunk/Build.Release/bin/digicam_server'] + list_param
        #list_param = ['sudo','/data/software/DAQ/CamerasToACTL/Build.Release/bin/digicam_server'] + list_param
        str_param = ''
        for p in list_param:
            str_param = str_param + p + ' '
        self.log.info('Running %s' % str_param)

        self.camera_server = Popen(str_param, stdout=PIPE, stderr=STDOUT,shell=True)#,preexec_fn=os.setsid)
        # env=dict(os.environ, my_env_prop='value'))
        if not self.log_queue : self.log_queue = Queue()
        if not self.stop_event: self.stop_event= Event()
        self.log_thread = Thread(target=self.enqueue_output, args=(self.log_queue ,self.camera_server.stdout,self.stop_event))
        self.log_thread.daemon = True  # thread dies with the program
        self.stop_event.clear()
        self.log_thread.start()


        return

    def stop_server(self):
        try :
            p = Popen('sudo kill %d'%(int(self.camera_server.pid)), stdout=PIPE, stderr=STDOUT,shell=True)
            p.wait()
            self.camera_server.wait()
        except Exception:
            self.camera_server.wait()
        self.stop_event.set()
        self.log_thread.join()

        #p = Popen('sudo kill %d'%(int(self.camera_server.pid)+6), stdout=PIPE, stderr=STDOUT,shell=True)
