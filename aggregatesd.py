import csv
import os
from decimal import *
import collections    

class SecondaryDataAggregator():
    def __init__(self, secondaryDataFilename, isVerbose):
        '''
        Constructs an instance of Notifyer which computes the secndary data.
 
        :param filename: name of the file to write in.
        :param isVerbose: if True, outputs received data in console
        '''
 
        #creating the output csv file and initializing it with the column titles
        #self.archiver = Archiver(secondaryDataFilename, isVerbose=False)
        self.isVerbose = isVerbose
        #self.criterion = PriceVolumeCriterion()
        
        self.isOneSecondIntervalReached = False
        
        self.secondaryDataIndex = -1
        self.lastSecBeginTimestamp = 0
        self.lastSecVolume = 0
        self.lastSecAvgPrice = 0
        self.lastSecTradeNumber = 0

        self.lastSecMovingVolume = 0
        self.lastSecMovingAvgPrice = 0
        self.lastSecMovingTradeNumber = 0

    def update(self, data):
        recordIndex = ''
 
        if len(data) == 4:
            # data comming from archive file (mode simulation)
            recordIndexStr, timestampMilliSecStr, volumeFloatStr, priceFloatStr = data
        else:
            # data comming from exchange (mode real time)
            timestampMilliSecStr, volumeFloatStr, priceFloatStr = data
        
        timestampMilliSec = int(timestampMilliSecStr)
        priceFloat = float(priceFloatStr)
        volumeFloat = float(volumeFloatStr) 
        sdIndex, sdTimestamp, sdTradeNumber, sdVolumeFloat, sdPricefloat = self.aggregateSecondaryData(timestampMilliSec, priceFloat, volumeFloat)
 
        #calling the criterion to check if it should raise an alarm
        #criterionData = self.criterion.check(secondaryData)
 
        # sending the secondary data to the archiver so that the sd are written in the
        # sd file to enable viewing them in a price/volume chart. Note that the archiver
        # takes care of implementing the secondary data record index.
        #self.archiver.update(secondaryData + criterionData)
 
        if self.lastSecBeginTimestamp == 0:
            self.lastSecBeginTimestamp = timestampMilliSec
      
        if self.isOneSecondIntervalReached and self.secondaryDataIndex > 0:
            print("{0}\t{1}\t{2}\t{3:.7f}\t{4:.2f}".format(sdIndex, sdTimestamp, sdTradeNumber, sdVolumeFloat, sdPricefloat))
            self.lastSecBeginTimestamp += 1000
            self.isOneSecondIntervalReached = False
            self.lastSecTradeNumber = 0
            self.lastSecVolume = 0
            self.lastSecAvgPrice = 0 
        #SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...
 
 
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
        
        self.lastSecTradeNumber += 1
        self.lastSecVolume += volumeFloat
        self.lastSecAvgPrice += priceFloat * volumeFloat
                
        if timestampMilliSec >= self.lastSecBeginTimestamp:
            self.isOneSecondIntervalReached = True
            self.secondaryDataIndex += 1
            
            return self.secondaryDataIndex, self.lastSecBeginTimestamp, self.lastSecTradeNumber, self.lastSecVolume, self.lastSecAvgPrice / self.lastSecVolume
        else:
            return 0, None, None, None, None

dir_path = os.path.dirname(os.path.realpath(__file__))
primaryFileName = "primary.csv"
sd_file = open(dir_path + "/" + primaryFileName, 'r')
sd_reader = csv.reader(sd_file, delimiter='\t')
next(sd_reader) #read the header line

secDataAggregator = SecondaryDataAggregator(None,True)

#print('Index\tTime\t\tVolume\t\tPrice')
print('Idx\tTime\t\tTrades\tVolume\t\tPrice')

for data in sd_reader:
    secDataAggregator.update(data)
