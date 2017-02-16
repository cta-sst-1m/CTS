# Installation

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
Need to run under python2 (because of the IXXAT libraries).
On this machine, activate the python2.7 environement and the python-can libraries: 

```
source activate root6_p2
canSST1M
```

Start by running the server

```
python ctsopcua/cts_opcua_server.py angle

```

where angle can be 0,120,240

## CTS Control
Then in another console run the client, it can actually run on any python version (prefer 3)

```
source activate ctapipe
```

```
python CTSControl.py angle

```

when launching the client the various functionnalities are detailed

or the more advanced

```
python RunManager.py -y theyamlfile
```
