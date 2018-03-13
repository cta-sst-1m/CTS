The full documentation can be found at https://github.com/cta-sst-1m/CTS/wiki

In the following you can find quick installation and usage procedure


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
Start by running the server

```
$ source activate ctapipe
```

```
(ctapipe) $ python cts_opcua/cts_opcua_server.py angle

```

where angle can be 0,120,240

## CTS Control
Then in another console run the client

```
$ source activate ctapipe
```

```
(ctapipe) $ python CTSControl.py angle

```

when launching the client the various functionnalities are detailed

or the more advanced

```
python RunManager.py -y theyamlfile
```
