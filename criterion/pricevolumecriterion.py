from criterion.criterion import Criterion
from documentation.seqdiagbuilder import SeqDiagBuilder

class PriceVolumeCriterion(Criterion):
    '''
    :seqdiag_note Responsible of computing if an alarm must be raised.
    '''
    def check(self, data):
        '''
        Check if the criterion is reached.

        :seqdiag_note method to be implemented by Philippe
        '''
        SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...


if __name__ == '__main__':
    pass