from observer.observer import Observer
from documentation.seqdiagbuilder import SeqDiagBuilder
import csv

class Archiver(Observer):
    '''
    :seqdiag_note In simulation mode, this Observer (Archiver, like SecondaryData Aggregator, inherits from Observer) writes the secondary data on disk. In real time mode, saves on disk the primary data.
    '''
    CSV_ROW_HEADER = ["INDEX", "MS TIMESTAMP", "PRICE", "VOLUME"]

    '''
    This class stores the received data into a csv file.
    '''
    def __init__(self, filename, isVerbose):
        '''
        Constructs an instance of Archiver which will write into the passed
        file name. In case the file already exists, it will be overwritten.

        :param filename: name of the file to write in.
        :param isVerbose: if True, outputs received data in console
        '''

        #creating the output csv file and initializing it with the column titles
        self.filename = filename
        self.file = open(self.filename, 'w', newline = '')
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.CSV_ROW_HEADER)
        self.isVerbose = isVerbose
        self.recordIndex = 0

    def update(self, data):
        self.recordIndex += 1
        timestampMilliSecCriterion = -1
        priceFloatCriterion = -1
        volumeFloatCriterion = -1
        if len(data) == 6:
            # data comming from archive file (mode simulation)
            timestampMilliSec, priceFloat, volumeFloat, timestampMilliSecCriterion, priceFloatCriterion, volumeFloatCriterion = data
        else:
            # data comming from exchange (mode real time)
            timestampMilliSec, priceFloat, volumeFloat = data

        self.writer.writerow([self.recordIndex, timestampMilliSec, priceFloat, volumeFloat, timestampMilliSecCriterion, priceFloatCriterion, volumeFloatCriterion])

        if self.isVerbose:
            print("{} {} {} {}".format(self.recordIndex, timestampMilliSec, priceFloat, volumeFloat, timestampMilliSecCriterion, priceFloatCriterion, volumeFloatCriterion))

        SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...

    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.file.close()
        print('Archiver on file {} closed'.format(self.filename))
