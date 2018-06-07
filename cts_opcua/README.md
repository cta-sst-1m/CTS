# OpcUa structure

* CTS: addr="ns=2, s=CTS", parent node.

* time: addr="ns=2, s=CTS.time", type=int, Node containing server timestamp

## `DAC` folder

 *  `set_all(dc_level, ac_level)`: 
 
    addr="ns=2, s=CTS.DAC.set_all"
    
    Function to set dc_level and ac_level for all LEDs. 
    Very fast as it uses broadcast.
    
    Parameters:
  
    * dc_level: type=int, DAC level for the DC LEDs, from 0 to 1023.
    * ac_level: type=int, DAC level for the AC LEDs, from 0 to 1023.
  
### `AC` folder
 
 * `patches`: addr="ns=2, s=CTS.DAC.AC.patches", type="list of 432 ints", Node containing DAC values for all AC patches.
 * `set_halfBoard(halfBoard, ac_level)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_halfBoard"
    
    Function to set ac_level for the given LED half board. 
    
    Parameters:
  
    * halfBoard: type=int, LED half board number, from 0 to 53.
    * ac_level: type=int, DAC level for the AC LEDs, from 0 to 1023.
 * `set_patch(patch, ac_level)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_patch"
    
    Function to set the AC level for the given LED patch. 
    
    Parameters:
  
    * patch: type=int, LED patch number, from 0 to 431.
    * ac_level: type=int, DAC level for the AC LEDs, from 0 to 1023.
 * `set_patches(levels_json)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_patches"
    
    Function to set the AC level for all LED patches. Quite slow (~1 min) as patches are set sequentially.
    
    Parameters:
  
    * levels_json: type=string, JSON encoded list of 432 DAC values, one per patch.
  * `set_pixels(levels_json)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_pixels"
    
    Function to set the AC level for all camera pixels. 
    The values of the 3 pixels of each patches are averaged.
    Quite slow (~1 min) if the values are different for each patch.
    Optimized to set DAC values for the half board if all patches of the half board have the same values.
    
    Parameters:
  
    * levels_json: type=string, JSON encoded list of 1296 DAC AC levels, one per camera pixels. 
### `DC` folder
 
 * `boards`: addr="ns=2, s=CTS.DAC.AC.boards", type="list of 27 ints", Node containing DAC values for all DC boards.
 * `set_board(board, dc_level)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_board"
    
    Function to set the DC level for the given LED board. 
    
    Parameters:
  
    * board: type=int, LED board number, from 0 to 26.
    * dc_level: type=int, DAC level for the DC LEDs, from 0 to 1023.
 * `set_boards(levels_json)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_boards"
    
    Function to set the DC for all LED boards.
    
    Parameters:
  
    * levels_json: type=string, JSON encoded list of 27 DAC values, one per board.
  * `set_pixels(levels_json)`: 
 
    addr="ns=2, s=CTS.DAC.AC.set_pixels"
    
    Function to set the DC level for all camera pixels. 
    The values of the pixels of each boards are averaged.
    
    Parameters:
  
    * levels_json: type=string, JSON encoded list of 1296 DAC DC levels, one per camera pixels.
    
## `DACoffset` folder
As the [DAC](#dac-folder) folder, but showing the DAC offset levels instead of DAC levels.
  
## `mapping` folder
  * boards_to_pixels: addr="ns=2, s=CTS.mapping.boards_to_pixels", type="2D list of int, shape=(27,48)", 
    Node containing the 48 camera pixels indexes for each of the 27 LED boards.
  * pixels_to_boards: addr="ns=2, s=CTS.mapping.pixels_to_boards", type="list of 1296 ints", 
    Node containing the LED board indexes for each of the 1296 pixels.
  * halfBoards_to_pixels: addr="ns=2, s=CTS.mapping.boards_to_pixels", type="2D list of int, shape=(54,24)", 
    Node containing the 24 camera pixels indexes for each of the 54 LED half-boards.
  * pixels_to_halfBoards: addr="ns=2, s=CTS.mapping.pixels_to_halfBoards", type="list of 1296 ints", 
    Node containing the LED half-board indexes for each of the 1296 pixels.
  * patches_to_pixels: addr="ns=2, s=CTS.mapping.patches_to_pixels", type="2D list of int, shape=(432,3)", 
    Node containing the 3 camera pixels indexes for each of the 432 LED patches.
  * pixels_to_patches: addr="ns=2, s=CTS.mapping.pixels_to_patches", type="list of 1296 ints", 
    Node containing the LED patch indexes for each of the 1296 pixels.
  * halfBoards_to_patches: addr="ns=2, s=CTS.mapping.halfBoards_to_patches", type="2D list of int, shape=(54,8)", 
    Node containing the 8 LED patch indexes for each of the 54 LED half-boards.
  * patches_to_halfBoards: addr="ns=2, s=CTS.mapping.patches_to_halfBoards", type="list of 342 ints", 
    Node containing the LED half-board indexes for each of the 432 patches.
   
## `status` folder
### `AC` folder
 * `status`: addr="ns=2, s=CTS.status.AC.status", type="list of 1296 bools", Node containing status (True: ON, False: OFF) 
    of AC LEDs for each camera pixel.
 * `set_leds_in_halfBoard(halfBoard, status)`: 
 
    addr="ns=2, s=CTS.status.AC.set_leds_in_halfBoard"
    
    Function to set the status of the 24 AC LEDs for the given LED half-board.
    
    Parameters:
  
    * halfBoard: type=int, LED half-board number, from 0 to 53.
    * status: type=int, in binary, each bit of status represent the status of a LED in the given half-board. For example:
        * status=0 means all LEDs are off
        * status=4(=0b000000000000000000000100) means all LEDs are off except the 3rd.
        * status=16777215(=0b11111111111111111111111111)  means all LEDs are on.
 * `set_pixels(status_json)`: 
 
    addr="ns=2, s=CTS.status.AC.set_pixels"
    
    Function to set the status of all AC LEDs.
    
    Parameters:
     
    * levels_json: type=string, JSON encoded list of 1296 DAC AC status(0: OFF, 1: ON), one per camera pixels.
### `DC` folder
 same as [AC folder](#ac-folder-1) but with status of the AC LEDs instead of DC LEDs.
