# Get some OpcUa staff
from opcua import Client


class DigiCamClient:
    """
    DigiCamClient class is the OpcUa client for the DigiCam OpcUa server.

    """

    def __init__(self):
        """
        Initialise function for DigiCamClient

        """

        self._function_list = {}
        self.client = Client("opc.tcp://129.194.55.153:12686/digicam", timeout=10000)

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

    def client_off(self):
        """
        client_off()

        Call the necessary step to exit the client
        """
        # disconnect
        self.client.disconnect()

    def start_trigger(self):
        """
        start_trigger()

        Call the necessary functions to start the trigger in DigiCam

        :return:
        """
        return

    def stop_trigger(self):
        """
        stop_trigger()

        Call the necessary functions to stop the trigger in DigiCam

        :return:
        """
        return

    def start_run(self):
        """

        :return:
        """
        return

    def stop_run(self):
        """

        :return:
        """
        return

    def start_writer(self):
        """

        :return:
        """
        return

    def stop_writer(self):
        """

        :return:
        """
        return
