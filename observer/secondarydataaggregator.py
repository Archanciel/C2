from observer.observer import Observer
from observer.archiver import Archiver
from criterion.pricevolumecriterion import PriceVolumeCriterion
from documentation.seqdiagbuilder import SeqDiagBuilder

class SecondaryDataAggregator(Observer):
    '''
    This class ...

    :seqdiag_note Implements the Observer part in the Observable design pattern. Calculates the secondary data and sends them one by one to the Criterion.
    '''
    def __init__(self, secondaryDataFilename, isVerbose):
        '''
        Constructs an instance of Notifyer which computes the secndary data.

        :param filename: name of the file to write in.
        :param isVerbose: if True, outputs received data in console
        '''

        #creating the output csv file and initializing it with the column titles
        self.archiver = Archiver(secondaryDataFilename, isVerbose=False)
        self.isVerbose = isVerbose
        self.criterion = PriceVolumeCriterion()


    def update(self, data):
        recordIndex = ''

        if len(data) == 4:
            # data comming from archive file (mode simulation)
            recordIndex, timestampMilliSec, priceFloat, volumeFloat = data
        else:
            # data comming from exchange (mode real time)
            timestampMilliSec, priceFloat, volumeFloat = data

        secondaryData = False

        while not secondaryData:
            secondaryData = self.aggregateSecondaryData(timestampMilliSec, priceFloat, volumeFloat)

        # sending the secondary data to the archiver so that the sd are written in the
        # sd file to enable viewing them in a price/volume chart. Note that the archiver
        # takes care of implementing the secondary data record index.
        self.archiver.update(secondaryData)

        #calling the criterion to check if it should raise an alarm
        self.criterion.check(secondaryData)



        if self.isVerbose:
            print("SecondaryDataAggregator: {} {} {} {}".format(recordIndex, timestampMilliSec, priceFloat, volumeFloat))

        SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...


    def aggregateSecondaryData(self, timestampMilliSec, priceFloat, volumeFloat):
        '''
        This method is called each time primary data are received. It aggregates the passed
        primary data and returns None if the aggregation interval (typically 1 second9 is not
        reached or the tuple timestampMilliSec, priceFloat, volumeFloat once data
        for the aggregation interval was reached.

        :seqdiag_note method to be implemented by Philippe

        :param timestampMilliSec:
        :param priceFloat:
        :param volumeFloat:
        :return: timestampMilliSec, priceFloat, volumeFloat
        '''

        SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...

        return timestampMilliSec, priceFloat, volumeFloat # temporally returning silly value !


    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.archiver.close()
        print('SecondaryDataAggregator closed')
