import utils.fsm_def
from fysom import Fysom
import cts_fsm
import logging

class CTSMaster(Fysom):
    '''
    CTSMaster implements the FSM which control the experimental setup

    '''
    def __init__( self , elements = ['generator'] , fsm_table = utils.fsm_def.FSM_TABLE ) :
        '''
        :param elements: list of hardware elements to be taken into account in the setup
        '''

        # FSM allocation
        Fysom.__init__( self , fsm_table )

        # Define elements
        self.elements = self._append_elements(elements)

        # logger TODO name file with time
        self.logger = logging.basicConfig(filename='myapp.log', level=logging.DEBUG)



    def _append_elements(self, elements):
        '''
        append_elements is a function to append to the master the elements to be controlled
        :param elements: list of element names to include
        :return: dictionnaries of element instance
        '''

        # dictionnary to return
        element_dictionnary = {}

        # loop over elements of the setup
        for element in elements:
            if element == 'generator':
                # TODO allocation address in a pickle or database
                element_dictionnary[element] =  cts_fsm.generator_fsm()

        return element_dictionnary


    def allocate(self):
        '''

        :return:
        '''
        for element_name, element in self.elements.items():
            print('allocate the %s'%element_name)
            element.allocate()





