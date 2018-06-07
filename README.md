In the following you can find quick installation and usage procedure


# Installation

## Create a conda environement

### Install anaconda (if you don't have anaconda)

```
  wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
  bash miniconda.sh -b -p
  conda update -q conda
```

### Create a conda environement

```
conda env create -f environment.yml
source activate cts
```
## Install requirements

pip install -r requirements.txt


build and install python-opcua as in OpcUaCameraSlowControl/python-opcua

build and install python-can as in OpcUaCameraSlowControl/BUS-SST1M

then run

```
python setup.py build

```

and eventually if you need to integrate it to your environement

```
python setup.py install

```

# Usage

## CTS OpcUa Server
Start by running the server

```
$ source activate ctapipe
```

```
(ctapipe) $ python cts_opcua/cts_opcua_server.py angle

```

where angle can be 0, 120 or 240.

As soon as `WARNING:opcua.server.binary_server_asyncio:Listening on 0.0.0.0:4843` is shown, you can control the CTS with any OpcUa client which is compatible with methods.
The structure of the OpcUa server is discribed in [cts_opcua/README.md](cts_opcua/README.md) 

## CTS ACS component
Once the OpcUa server is running, an ICS interface is available as well.
see [cts_acs/README.md](cts_acs/README.md) for more details.
