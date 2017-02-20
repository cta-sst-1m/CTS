from distutils.core import setup

setup(
    name='CameraTestSetup',
    version='',
    packages=['cts_core', 'cts_opcua','cts_can','setup_fsm','setup_components','utils'],
    url='',
    license='',
    author='cocov',
    author_email='victor.coco@cern.ch',
    description='', requires=['ctapipe', 'IPython', 'fysom']
)
