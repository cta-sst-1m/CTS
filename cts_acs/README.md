# Alma Control System for Camera Test setup
An implementation of the Alma Control System (ACS) for the Camera Test setup (CTS).

# Instalation
## requirements
* ACS must be installed (that is the case on SST1M_server and PDP_server).
* the OpcUa server must be running before starting the ACS container.

## Specify the address of the OpcUa server
edit the `CTS/cts_acs/test/CDB/alma/CTSArrayControlSystem/CTSArrayControlSystem.xml` file.

change the line `opc_uri="opc.tcp://?:?/cameraslowcontrol/server/"` replacing ? with the IP address and the port of the CTS OpcUa server.

## compilation    
run the activate_ACS bash function:

    1. Start the environment with:
        activate_ACS
    
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
<_ Name="CTSArrayControlSystem"  Code="cta.ctsarraycontrolsystemsst.CTSArrayControlSystemImpl.CTSArrayControlSystemComponentHelper" Type="IDL:cta/ctsarraycontrolsystemsst/CTSArrayControlSystem:1.0" Container="ctsContainer" ImplLang="java"/>
```

## update SST1M master
ACS functions are available through the master once added to the subsystems.
To update the CTS subsystem copy the cts_acs/MasterSST1M/cts.py file to the subsystems folder
(/home/ctauser/software/control/master/MasterSST1M/src/sstmaster/subsystems on the pdp server).

## Use the container
* Start `acscommandcenter`
* Ensure `ctsContainer` is in the container list (add if it is not).
* Ensure CTS OpcUa server is running (see [../README.md](../README.md)).
* Start the `ctsContainer` by clicking the green arrow on the right.
The CTS can now be controled by ACS script or using an ACS client (`objexp` for example).

# ACS Container structure

## variables

* opcuaTime: timestamp given by the OpcUa server.
* boards_DC_DAC: Values of the DC DAC level for all LED boards (27 ints).
* boards_DC_offset: Values of the DC DAC offset for all LED boards (27 ints).
* patches_AC_DAC: Values of the AC DAC level for all LED patches (432 ints).
* patches_AC_offset: Values of the AC DAC offset for all LED patches (432 ints).
* pixels_AC_status: Status of each of the AC LED (0:OFF, 1:ON) (1296 ints)
* pixels_DC_status: Status of each of the DC LED (0:OFF, 1:ON) (1296 ints)
* patches_to_halfBoards: index of the LED patch for each of the camera pixels (1296 ints).
* pixels_to_boards: index of the LED board for each of the camera pixels (1296 ints).
* pixels_to_halfBoards: index of the LED half-board for each of the camera pixels (1296 ints).
* pixels_to_patches: index of the LED patch for each of the camera pixels (1296 ints).

## functions

* set_all_DAC(inLevelDC, inLevelAC): function to set the same AC and DC DAC levels to all LEDs. Fast as it uses broadcast.

    parameters:
    
    * inLevelDC: DC DAC level to set to all LEDs (int, between 0 and 1023)
    * inLevelAC: AC DAC level to set to all LEDs (int, between 0 and 1023)
    
* set_all_offset(inOffsetDC, inOffsetAC): function to set the same AC and DC DAC offsets to all LEDs. Fast as it uses broadcast.

    parameters:
    
    * inOffsetDC: DC DAC offset to set to all LEDs (int, between 0 and 1023)
    * inOffsetAC: AC DAC offset to set to all LEDs (int, between 0 and 1023)
    
* set_board_DC_DAC(inBoard, inLevel): function to set the DC DAC level for the indicated LED board.

    parameters:
    
    * inBoard: index of the LED board (int, between 0 and 26)
    * inLevel: DC DAC level to set (int, between 0 and 1023)
    
* set_board_DC_offset(inBoard, inOffset): function to set the DC DAC offset for the indicated LED board.

    parameters:
    
    * inBoard: index of the LED board (int, between 0 and 26)
    * inOffset: DC DAC offset to set (int, between 0 and 1023)
* set_boards_DC_DAC(inBoardsLevel): function to set the DC DAC values for all LED boards.

    parameters:
    
    * inBoardsLevel: JSON encoded list of 27 DC DAC levels (int, between 0 and 1023), one for each LED board.
* set_boards_DC_offset(inBoardsOffset): function to set the DC DAC offsets for all LED boards.

    parameters:
    
    * inBoardsOffset: JSON encoded list of 27 DC DAC offsets (int, between 0 and 1023), one for each LED board. 
* set_halfBoard_AC_DAC(inHalfBoard, inLevel): function to set the AC DAC level for the given LED half-board.

    parameters:
    
    * inHalfBoard: index of the LED half-board (int, between 0 and 53)
    * inLevel: AC DAC level to set (int, between 0 and 1023)
* set_halfBoard_AC_offset(inHalfBoard, inOffset): function to set the AC DAC offset for the given LED half-board.

    parameters:
    
    * inHalfBoard: index of the LED half-board (int, between 0 and 53)
    * inOffset: AC DAC offset to set (int, between 0 and 1023)
* set_leds_AC_in_halfBoard_status(inHalfBoard, inHalfBoardStatus): function to set the AC LED status for the given LED half-board.

    parameters:
    
    * inHalfBoard: index of the LED half-board (int, between 0 and 53)
    * inHalfBoardStatus: in binary, each bit of inHalfBoardStatus represents the status of a AC LED in the given half-board (int, between 0 and 16777215). For example:
        * inHalfBoardStatus=0 means all LEDs are off
        * inHalfBoardStatus=4(=0b000000000000000000000100) means all LEDs are off except the 3rd.
        * inHalfBoardStatus=16777215(=0b11111111111111111111111111)  means all LEDs are on.
* set_leds_DC_in_halfBoard_status(inHalfBoard, inHalfBoardStatus): function to set the AC LED status for the given LED half-board. 

    parameters:
    
    * inHalfBoard: index of the LED half-board (int, between 0 and 53)
    * inHalfBoardStatus: in binary, each bit of inHalfBoardStatus represents the status of a DC LED in the given half-board (int, between 0 and 16777215). For example:
        * inHalfBoardStatus=0 means all LEDs are off
        * inHalfBoardStatus=4(=0b000000000000000000000100) means all LEDs are off except the 3rd.
        * inHalfBoardStatus=16777215(=0b11111111111111111111111111)  means all LEDs are on.
* set_patch_AC_DAC(inPatch, inLevel): function to set the DAC level for the AC LEDs of the given patch.

    parameters:
    
    * inPatch: index of the LED patch (int, between 0 and 431)
    * inLevel: DAC level of the AC LEDs (int, between 0 and 1023)
* set_patch_AC_offset(inPatch, inOffset): function to set the DAC offset for the AC LEDs of the given patch.

    parameters:
    
    * inPatch: index of the LED patch (int, between 0 and 431)
    * inOffset: DAC offset of the AC LEDs (int, between 0 and 1023)
* set_patches_AC_DAC(inPatchesLevel): function to set the AC DAC values for all LED patches.

    parameters:
    
    * inBoardsLevel: JSON encoded list of 432 AC DAC levels (int, between 0 and 1023), one for each LED patch.
* set_patches_AC_offset(inPatchesOffset): function to set the AC DAC offsets for all LED patches.

    parameters:
    
    * inBoardsOffset: JSON encoded list of 432 AC DAC offsets (int, between 0 and 1023), one for each LED patch.
* set_pixels_AC_DAC(inPixelsLevel): function to set the AC DAC values for all LED pixels. Values for the 3 LEDs of each pach are averaged. 
Quite slow (~1 min) if the values are different for each patch. 
Optimized to set DAC values for the half board if all patches of the half board have the same values.

    parameters:
    
    * inPixelsLevel: JSON encoded list of 1296 AC DAC levels (int, between 0 and 1023), one for each camera pixel.
* set_pixels_AC_offset(inPixelsOffset): function to set the AC DAC offsets for all LED pixels. Values for the 3 LEDs of each pach are averaged. 
Quite slow (~1 min) if the offsets are different for each patch. 
Optimized to set DAC offsets for the half board if all offsets of the half board have the same values.

    parameters:
    
    * inPixelsOffset: JSON encoded list of 1296 AC DAC offsets (int, between 0 and 1023), one for each camera pixel.
* set_pixels_AC_status(inPixelsStatus): function to set the status of AC LED for each camera pixel.

    parameters:
    
    * inPixelsStatus: JSON encoded list of 1296 AC LED status (bool), one for each camera pixel.
* set_pixels_DC_DAC(inPixelsLevel): function to set the DC DAC values for all LED pixels. Values for the 48 LEDs of each board are averaged. 

    parameters:
    
    * inPixelsLevel: JSON encoded list of 1296 DC DAC levels (int, between 0 and 1023), one for each camera pixel.
* set_pixels_DC_offset(inPixelsOffset): function to set the DC DAC offsets for all LED pixels. Values for the 48 LEDs of each board are averaged. 

    parameters:
    
    * inPixelsOffset: JSON encoded list of 1296 DC DAC offsets (int, between 0 and 1023), one for each camera pixel.
* set_pixels_DC_status(inPixelsStatus): function to set the status of DC LED for each camera pixel.

    parameters:
    
    * inPixelsStatus: JSON encoded list of 1296 DC LED status (bool), one for each camera pixel.
