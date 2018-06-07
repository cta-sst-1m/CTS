# Alma Control System for Camera Test setup
An implementation of the Alma Control System (ACS) for the Camera Test setup (CTS).

# Instalation
## requirements
* ACS must be installed (that is the case on SST1M_server and PDP_server).
* the OpcUa server must be running while the 

## compilation    
run the activate_ACS bash function:
    1. Start the environment with:
        source ./activate_ACS.sh
    
    2. go into the src/ folder with:
        cd src

    3. compile with:
        make

    4. optional: install globally with:
        make install

## Add component to the Configuration Database
To create an entry for your component in the Configuration Database,
copy the line below into a new entry in the file $ACS_CDB/MACI/Components/Components.xml:
```
<_ Name="CTSArrayControlSystem"              Code="cta.ctsarraycontrolsystemsst.CTSArrayControlSystemImpl.CTSArrayControlSystemComponentHelper"              Type="IDL:cta/ctsarraycontrolsystemsst/CTSArrayControlSystem:1.0" Container="ctsContainer" ImplLang="java" />
```

## Use the container
Start `acscommandcenter` and ensure `ctsContainer` is in the container list (add if it is not).
Ensure CTS OpcUa server is running (see [../README.md](../README.md)).
Start the `ctsContainer` by clicking the green arrow on the right.
The CTS can now be controled by ACS script or using an ACS client (`objexp` for example).


