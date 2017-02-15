from distutils.core import setup

setup(
    name='CameraTestSetup',
    version='',
    packages=['cts', 'cts_opcua','cts_can','cts_fsm','digicam_opcua','utils','data_aquisition','generator'],
    url='',
    license='',
    author='cocov',
    author_email='victor.coco@cern.ch',
    description='', requires=['ctapipe', 'IPython', 'fysom']
)
