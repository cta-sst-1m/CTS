from AcsWorker import ACSWorker
from enum import Enum
import json

def _JSONize(argument):
    if isinstance(argument, str):
        return argument
    else:
        return json.dumps(argument)


class CTS:
    def __init__(self, component_name, client="MasterClient", sticky=True, acsClient=None):
        self.component_name = component_name
        self.acs = ACSWorker(client + "::" + self.component_name, sticky=sticky, extraModules=[], acsClient=acsClient)
        self.log = self.acs.log
        self.acs.connectComponent(self.component_name)
        self.acs.processCharacteristics()
        self.acs.oncleanup = self.cleanup
        
    def disconnect(self):
        self.acs.cleanup()
        
    def cleanup(self):
        pass

    #CORBA methods

    def set_all_DAC(self, inLevelDC, inLevelAC):
        return self.acs._nonconfirmed_execute("set_all_DAC", inLevelDC, inLevelAC)

    def set_all_offset(self, inOffsetDC, inOffsetAC):
        return self.acs._nonconfirmed_execute("set_all_offset", inOffsetDC, inOffsetAC)

    def set_board_DC_DAC(self, inBoard, inLevel):
        return self.acs._nonconfirmed_execute("set_board_DC_DAC", inBoard, inLevel)

    def set_board_DC_offset(self, inBoard, inOffset):
        return self.acs._nonconfirmed_execute("set_board_DC_offset", inBoard, inOffset)

    def set_halfBoard_AC_DAC(self, inHalfBoard, inLevel):
        return self.acs._nonconfirmed_execute("set_halfBoard_AC_DAC", inHalfBoard, inLevel)

    def set_halfBoard_AC_offset(self, inHalfBoard, inOffset):
        return self.acs._nonconfirmed_execute("set_halfBoard_AC_offset", inHalfBoard, inOffset)

    def set_leds_AC_in_halfBoard_status(self, inHalfBoard, inHalfBoardStatus):
        return self.acs._nonconfirmed_execute("set_leds_AC_in_halfBoard_status", inHalfBoard, inHalfBoardStatus)

    def set_leds_DC_in_halfBoard_status(self, inHalfBoard, inHalfBoardStatus):
        return self.acs._nonconfirmed_execute("set_leds_DC_in_halfBoard_status", inHalfBoard, inHalfBoardStatus)

    def set_patch_AC_DAC(self, inPatch, inLevel):
        return self.acs._nonconfirmed_execute("set_patch_AC_DAC", inPatch, inLevel)

    def set_patch_AC_offset(self, inPatch, inOffset):
        return self.acs._nonconfirmed_execute("set_patch_AC_offset", inPatch, inOffset)

    # Following methods accept either an array or a JSON encoded string as argument.

    def set_boards_DC_DAC(self, inBoardsLevel):
        return self.acs._nonconfirmed_execute("set_boards_DC_DAC", _JSONize(inBoardsLevel))

    def set_boards_DC_offset(self, inBoardsOffset):
        return self.acs._nonconfirmed_execute("set_boards_DC_offset", _JSONize(inBoardsOffset))

    def set_patches_AC_DAC(self, inPatchesLevel):
        return self.acs._nonconfirmed_execute("set_patches_AC_DAC", _JSONize(inPatchesLevel))

    def set_patches_AC_offset(self, inPatchesOffset):
        return self.acs._nonconfirmed_execute("set_patches_AC_offset", _JSONize(inPatchesOffset))

    def set_pixels_AC_DAC(self, inPixelsLevel):
        return self.acs._nonconfirmed_execute("set_pixels_AC_DAC", _JSONize(inPixelsLevel))

    def set_pixels_AC_offset(self, inPixelsOffset):
        return self.acs._nonconfirmed_execute("set_pixels_AC_offset", _JSONize(inPixelsOffset))

    def set_pixels_AC_status(self, inPixelsStatus):
        return self.acs._nonconfirmed_execute("set_pixels_AC_status", _JSONize(inPixelsStatus))

    def set_pixels_DC_DAC(self, inPixelsLevel):
        return self.acs._nonconfirmed_execute("set_pixels_DC_DAC", _JSONize(inPixelsLevel))

    def set_pixels_DC_offset(self, inPixelsOffset):
        return self.acs._nonconfirmed_execute("set_pixels_DC_offset", _JSONize(inPixelsOffset))

    def set_pixels_DC_status(self, inPixelsStatus):
        return self.acs._nonconfirmed_execute("set_pixels_DC_status", _JSONize(inPixelsStatus))

    def set_all_status(self, inStatus):
        return self.acs._nonconfirmed_execute("set_all_status", inStatus)
