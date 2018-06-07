# Alma Control System for Camera Test setup
An implementation of the Alma Control System (ACS) for the Camera Test setup (CTS).

# Instalation
## requirements
ACS must be installed (that is the case on SST1M_server and PDP_server).

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
copy the line below into a new entry in the file $ACS_CDB/MACI/Components/Components.xml
and modify the instance name of the component and the container:

`Name="CHARACTERISTICCOMPONENT_1" Code="alma.ACS.CharacteristicComponentImpl.CharacteristicComponentComponentHelper" Type="IDL:alma/ACS/CharacteristicComponent:1.0" Container="frodoContainer" ImplLang="java"`

## connect to the server
check with `acscommandcenter` and `objexp` that all looks ok.


