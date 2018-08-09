from observer.observer import Observer
from observer.archiver import Archiver
from criterion.pricevolumecriterion import PriceVolumeCriterion
from documentation.seqdiagbuilder import SeqDiagBuilder
from datetime import datetime

class SecondaryDataAggregator(Observer):
    '''
    This class ...

    :seqdiag_note Implements the Observer part in the Observable design pattern. Each tima its update(data) method is called, it adds this data to the current secondary aggreagated data and sends the secondary data when appropriate to the Criterion calling its check() method.
    '''
    def __init__(self, secondaryDataFilename, doNotPrintOutput=False, isVerbose=False):
        '''
        Constructs an instance of Notifyer which computes the secndary data.

        :param filename: name of the file to write in.
        :param doNotPrintOutput: used to indicate that the computed secondary data must not be printed
               in the console. Used when C2 is started in RT mode with a duration specified. In this
               case, a count down string is output in the console and this would interfere with
               the output of secondary data.
        :param isVerbose: if True, outputs received data in console
        '''

        #creating the output csv file and initializing it with the column titles
        self.archiver = Archiver(secondaryDataFilename, Archiver.SECONDARY_DATA_CSV_ROW_HEADER, isVerbose=False)
        self.doNotPrintOutput = doNotPrintOutput
        self.isVerbose = isVerbose
        self.criterion = PriceVolumeCriterion()

        self.isOneSecondIntervalReached = False

        self.lastSecBeginTimestamp = 0
        self.lastSecEndTimestamp = 0
        self.lastSecVolume = 0
        self.lastSecPriceVolumeTotal = 0
        self.lastSecTradeNumber = 0

        print('Time\t\tTrades\tVolume\t\tPrice')

    def update(self, data):
        recordIndex = ''

        if len(data) == 4:
            # data comming from archive file (mode simulation)
            recordIndexStr, timestampMilliSecStr, volumeFloatStr, priceFloatStr = data
        else:
            # data comming from exchange (mode real time)
            timestampMilliSecStr, volumeFloatStr, priceFloatStr = data

        timestampMilliSec = int(timestampMilliSecStr)

        if self.lastSecBeginTimestamp == 0:
            startTimestamp = self.calculateStartTimestamp(timestampMilliSec)
            self.lastSecBeginTimestamp = startTimestamp
            self.lastSecEndTimestamp = startTimestamp + 1000
            self.lastSecTradeNumber = 0
            self.lastSecVolume = 0
            self.lastSecPriceVolumeTotal = 0
        else:
            priceFloat = float(priceFloatStr)
            volumeFloat = float(volumeFloatStr)
            lastNotifiedPriceFloat = priceFloat
            lastNotifiedVolumeFloat = volumeFloat
            secondary_data = self.aggregateSecondaryData(timestampMilliSec, priceFloat, volumeFloat)
            if not secondary_data:
                return
            sdTimestamp, sdTradesNumber, sdVolumeFloat, sdPricefloat = secondary_data

            # calling the criterion to check if it should raise an alarm
            criterionData = self.criterion.check(data)

        if self.isOneSecondIntervalReached:
            # sending the secondary data to the archiver so that the sd are written in the
            # sd file to enable viewing them in a price/volume chart. Note that the archiver
            # takes care of implementing the secondary data record index.
#            self.archiver.update((sdTimestamp, sdTradesNumber, sdVolumeFloat, sdPricefloat) + criterionData)
            if sdPricefloat > 0:
                self.storeAndPrintSecondaryData(sdPricefloat, sdTimestamp, sdTradesNumber, sdVolumeFloat)

            while int(timestampMilliSec / 1000) * 1000 > self.lastSecEndTimestamp:
                sdTimestamp = self.lastSecEndTimestamp
                sdTradesNumber = 0
                sdVolumeFloat = 0

                if self.lastSecVolume > 0:
                    sdPricefloat = self.lastSecPriceVolumeTotal / self.lastSecVolume
                    self.storeAndPrintSecondaryData(sdPricefloat, sdTimestamp, sdTradesNumber, sdVolumeFloat)
                else:
                    # happens if no transaction were yet processed
                    sdPricefloat = 0

                self.lastSecBeginTimestamp += 1000
                self.lastSecEndTimestamp += 1000

            self.lastSecVolume = lastNotifiedVolumeFloat
            self.lastSecPriceVolumeTotal = lastNotifiedVolumeFloat * lastNotifiedPriceFloat
            self.lastSecTradeNumber += 1
            self.lastSecBeginTimestamp += 1000
            self.lastSecEndTimestamp += 1000
            self.isOneSecondIntervalReached = False

        SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...

    def storeAndPrintSecondaryData(self, sdPricefloat, sdTimestamp, sdTradesNumber, sdVolumeFloat):
        self.archiver.update((sdTimestamp, sdTradesNumber, sdVolumeFloat, sdPricefloat))
        if not self.doNotPrintOutput:
            timeHHMMSS = datetime.fromtimestamp(sdTimestamp / 1000).strftime('%H:%M:%S')
            print("{0}\t{1}\t\t{2:.6f}\t{3:.2f}".format(timeHHMMSS, sdTradesNumber, sdVolumeFloat,
                                                        sdPricefloat))

    def calculateStartTimestamp(self, timestampMilliSec):
        '''

        :param timestampMilliSec:
        :return:
        '''
        roundedTimestampMilliSec = int(timestampMilliSec / 1000) * 1000

        return roundedTimestampMilliSec + 1000

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

        if timestampMilliSec >= self.lastSecBeginTimestamp and timestampMilliSec < self.lastSecEndTimestamp:
            # here, the current primary data ts is within the current second frame
            self.lastSecTradeNumber += 1
            self.lastSecVolume += volumeFloat
            self.lastSecPriceVolumeTotal += priceFloat * volumeFloat

            return None, None, None, None
        elif timestampMilliSec >= self.lastSecEndTimestamp:
            if timestampMilliSec < self.lastSecEndTimestamp + 1000:
                # here, the current primary data ts is within the next second frame
                lastSecBeginTimestamp = self.lastSecBeginTimestamp
                lastSecTradeNumber = self.lastSecTradeNumber
                lastSecVolume = self.lastSecVolume

                if self.lastSecVolume > 0:
                    lastSecAvgPrice = self.lastSecPriceVolumeTotal / self.lastSecVolume
                else:
                    # happens if no transaction were yet processed, at start of RT or simulation
                    lastSecAvgPrice = 0

                self.lastSecTradeNumber = 1
                self.lastSecVolume = volumeFloat
                self.lastSecPriceVolumeTotal = priceFloat * volumeFloat
                self.lastSecBeginTimestamp += 1000
                self.lastSecEndTimestamp += 1000
                self.isOneSecondIntervalReached = True

                return lastSecBeginTimestamp, lastSecTradeNumber, lastSecVolume, lastSecAvgPrice
            else:
                # here, the current primary data ts is after the next second frame
                lastSecBeginTimestamp = self.lastSecBeginTimestamp
                lastSecTradeNumber = self.lastSecTradeNumber
                lastSecVolume = self.lastSecVolume

                if self.lastSecVolume > 0:
                    lastSecAvgPrice = self.lastSecPriceVolumeTotal / self.lastSecVolume
                else:
                    # happens if no transaction were yet processed, at start of RT or simulation
                    lastSecAvgPrice = 0

                self.isOneSecondIntervalReached = True

                return lastSecBeginTimestamp, lastSecTradeNumber, lastSecVolume, lastSecAvgPrice
        else:
            # here, the current primary data ts is before the current second frame. This
            # situation occurs at the very start of receiving the RT data or when processing
            # the first lines of the primary data input file in simulation mode when the ts
            # of those lines is before the ts calculated by the calculateStartTimestamp() method.
            # In this case, the line must simply be ignored.
            return None

    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.archiver.close()
        print('SecondaryDataAggregator closed')
