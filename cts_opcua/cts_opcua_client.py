# Get some OpcUa staff
from opcua import Client


class CTSClient():
    """
    CTSClient class is the OpcUa client for the CTS OpcUa server.

    It also contains various high level function allowing to turn on and off leds,
    run scans, display the CTS status, load MC events in the CTS, etc...

    Input:
          - angle_cts : the configuration of the CTS (0., 120. or 240. degrees )

    """

    def __init__(self):
        """
        Initialise function for CTSClient

        Input:
               - angle_cts : the configuration of the CTS (0., 120. or 240. degrees )

        """

        self._function_list = {}
        self.client = Client("opc.tcp://129.194.51.113:4843/cameratestsetup/server/", timeout=10000)
        self.client_on()


    def client_on(self):
        """
        client_on()

        Call the necessary step to start the client

        """
        # connect the client
        self.client.connect()
        # assign the functions to the client
        for folder in self.client.get_objects_node().get_child(["0:CTS"]).get_children():
            self._function_list[folder.get_browse_name().Name] = folder
        # set the DCDC values to ON (they are applied the first time when a level value is applied)
        self._dcdc_on()
        # prepare canvas
        # self._prepare_visualisation()
        # put all led to OFF and all level to 0
        # self.reset()
        # and plot it
        # self.plot()
        # self.plot()

    def client_off(self):
        """
        client_off()

        Call the necessary step to exit the client
        """
        # set the DCDC values to OFF (they are applied the first time when a level value is applied, ie in the reset)
        self._dcdc_off()
        # put all led to OFF and all level to 0
        # self.reset()
        # disconnect
        self.client.disconnect()

    # Functions published by the OpcUa server

    def set_dc_level(self, board, level):
        """
        set_dc_level( board , level )

        Interface to the  set_dc_level( board , level ) function of the OpcUa server
        which allows to set the DAC level of all DC LED in a LED board

        Input :
               - board : led board number (int 0-26)
               - level : DAC level (int 0-1023)
        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(self._function_list['set_dc_level'], board, level)

    def set_ac_level(self, patch, level):
        """
        set_ac_level( patch , level )

        Interface to the  set_ac_level( patch , level ) function of the OpcUa server which allows
        to set the DAC level of all AC LED in a LED patch

        Input :
               - board : patch number (int as in camera)
               - level : DAC level (int 0-1023)
        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(self._function_list['set_ac_level'], patch, level)

    def set_led_status(self, ledtype, pixel, status):
        """
        set_led_status( ledtype , pixel , status )

        Interface to the  set_led_status( ledtype , pixel , status ) function of the OpcUa server which allows
        to set the LED status (ie. active/inactive ) a given LED

        Input :
               - ledtype : type of led (str 'AC' or 'DC')
               - pixel   : pixel number (int as in camera)
               - status  : active or inactive (True/False, for AC led it will produce light only when recieving trigger)
        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(self._function_list['set_led_status'],
                                                                               ledtype, pixel, status)

    def all_on(self, ledtype, level):
        """
        Switch on all pixels of the given type and set them to level.
        Warning, due to hardware glich, it is necessary to set AC every time DC is set !
        Input :
               - ledtype : type of led (str 'AC' or 'DC')
               - level   : pixel number (int as in camera)
        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(self._function_list['all_on'],
                                                                               ledtype, level)


    def update(self):
        """
        update()

        Interface to the update_LEDparameters() function of the OpcUa server which will read in hardware the status
        of the leds, DAC levels and DCDC status

        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(
            self._function_list['update_LEDparameters'])

    def _dcdc_on(self):
        """
        _dcdc_on()

        Interface to the DCDC_ON() function of the OpcUa server which sets to ON the DCDC of all AC and DC in all board.
        Note that it only writes in the corresponding datapoint and only gets written in the hardware when set_led_status
        is called

        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(self._function_list['DCDC_ON'])

    def _dcdc_off(self):
        """
        _dcdc_off()

        Interface to the DCDC_OFF() function of the OpcUa server which sets to OFF the DCDC of all AC and DC in all
        board. Note that it only writes in the corresponding datapoint and only gets written in the hardware when
        set_led_status is called

        """
        return self.client.get_objects_node().get_child(["0:CTS"]).call_method(self._function_list['DCDC_OFF'])


if __name__ == "__main__":
    ctsclient = CTSClient()
    print('---|> The client have been started')
    print('---|> The client will be reset and turned off, wait...')
    ctsclient.client_off()
    print('---|> Done')
