from distutils.core import setup

setup(
    name='cts',
    version='1.0',
    packages=['cts_core', 'cts_opcua', 'cts_can'],
    url='https://github.com/cta-sst-1m/CTS',
    license='GPL',
    author='renier',
    author_email='yves.renier@unige.ch',
    description='Control system for the CTS (Camera Test Setup)',
)
