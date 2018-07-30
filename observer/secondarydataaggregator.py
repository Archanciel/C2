from observer.observer import Observer
from observer.archiver import Archiver
from criterion.pricevolumecriterion import PriceVolumeCriterion
from documentation.seqdiagbuilder import SeqDiagBuilder

class SecondaryDataAggregator(Observer):
    '''
    This class ...

    :seqdiag_note Implements the Observer part in the Observable design pattern. Each tima its update(data) method is called, it adds this data to the current secondary aggreagated data and sends the secondary data when appropriate to the Criterion calling its check() method.
    '''
    def __init__(self, secondaryDataFilename, isVerbose):
        '''
        Constructs an instance of Notifyer which computes the secndary data.

        :param filename: name of the file to write in.
        :param isVerbose: if True, outputs received data in console
        '''

        #creating the output csv file and initializing it with the column titles
        self.archiver = Archiver(secondaryDataFilename, Archiver.SECONDARY_DATA_CSV_ROW_HEADER, isVerbose=False)
        self.isVerbose = isVerbose
        self.criterion = PriceVolumeCriterion()

        self.isOneSecondIntervalReached = False

        self.lastSecBeginTimestamp = 0
        self.lastSecVolume = 0
        self.lastSecAvgPrice = 0
        self.lastSecTradeNumber = 0

    def update(self, data):
        recordIndex = ''

        if len(data) == 4:
            # data comming from archive file (mode simulation)
            recordIndexStr, timestampMilliSecStr, priceFloatStr, volumeFloatStr = data
        else:
            # data comming from exchange (mode real time)
            timestampMilliSecStr, priceFloatStr, volumeFloatStr = data

        timestampMilliSec = int(timestampMilliSecStr)
        priceFloat = float(priceFloatStr)
        volumeFloat = float(volumeFloatStr)
        sdTimestamp, sdTradesNumber, sdVolumeFloat, sdPricefloat = self.aggregateSecondaryData(
            timestampMilliSec, priceFloat, volumeFloat)

        # calling the criterion to check if it should raise an alarm
        criterionData = self.criterion.check(data)

        if self.lastSecBeginTimestamp == 0:
            self.lastSecBeginTimestamp = timestampMilliSec

        if self.isOneSecondIntervalReached and sdTimestamp > 0:
            # sending the secondary data to the archiver so that the sd are written in the
            # sd file to enable viewing them in a price/volume chart. Note that the archiver
            # takes care of implementing the secondary data record index.
#            self.archiver.update((sdTimestamp, sdTradesNumber, sdVolumeFloat, sdPricefloat) + criterionData)
            self.archiver.update((sdTimestamp, sdTradesNumber, sdVolumeFloat, sdPricefloat))

            print("\t{0}\t{1}\t\t{2:.7f}\t{3:.2f}".format(sdTimestamp, sdTradesNumber, sdVolumeFloat,
                                                               sdPricefloat))
            self.lastSecBeginTimestamp += 1000
            self.isOneSecondIntervalReached = False
            self.lastSecTradeNumber = 0
            self.lastSecVolume = 0
            self.lastSecAvgPrice = 0

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

        self.lastSecTradeNumber += 1
        self.lastSecVolume += volumeFloat
        self.lastSecAvgPrice += priceFloat * volumeFloat

        if timestampMilliSec >= self.lastSecBeginTimestamp:
            self.isOneSecondIntervalReached = True

            return self.lastSecBeginTimestamp, self.lastSecTradeNumber, self.lastSecVolume, self.lastSecAvgPrice / self.lastSecVolume
        else:
            return None, None, None, None

    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.archiver.close()
        print('SecondaryDataAggregator closed')
