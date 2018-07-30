from observer.observer import Observer
from documentation.seqdiagbuilder import SeqDiagBuilder
import csv

class Archiver(Observer):
    '''
    This class stores the received data into a csv file.

    :seqdiag_note In simulation mode, this Observer (Archiver, like SecondaryData Aggregator, inherits from Observer) writes the secondary data on disk. In real time mode, saves on disk the primary data.
    '''

    PRIMARY_DATA_CSV_ROW_HEADER = ["INDEX", "MS TIMESTAMP", "PRICE", "VOLUME"]
    SECONDARY_DATA_CSV_ROW_HEADER = ["INDEX", "TRADES", "MS TIMESTAMP", "PRICE", "VOLUME"]

    def __init__(self, filename, csvFileHeader, isVerbose):
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
        self.writer.writerow(csvFileHeader)
        self.isVerbose = isVerbose
        self.recordIndex = 0

    def update(self, data):
        SeqDiagBuilder.recordFlow() # called to build the sequence diagram. Can be commented out later ...

        self.recordIndex += 1

        try:
            if len(data) == 4:
                # data comming from archive file (mode simulation)
                timestampMilliSec, numberOfTrades, priceFloat, volumeFloat = data
                self.writer.writerow([self.recordIndex, numberOfTrades, timestampMilliSec, priceFloat, volumeFloat])

                if self.isVerbose:
                    print("{} {} {} {}".format(self.recordIndex, timestampMilliSec, priceFloat, volumeFloat))
            else:
                # data comming from exchange (mode real time)
                timestampMilliSec, priceFloat, volumeFloat = data
                self.writer.writerow([self.recordIndex, timestampMilliSec, priceFloat, volumeFloat])

                if self.isVerbose:
                    print("{} {} {} {}".format(self.recordIndex, timestampMilliSec, priceFloat, volumeFloat))
        except ValueError as e:
            '''
            This happens sometimes when C2 is started in mode RT for a specified duration.
            When the duration is reached, all the Observers, namely the Archivers, are closed 
            preamptively, which sometimes causes this exception due to a tentative to write the last 
            received data into an already closed file.
            '''
            if str(e) == 'I/O operation on closed file.':
                print('Last real time data received after closing {}. Consequence: {} not saved/processed !'.format(self.filename, data))
            else:
                raise e

    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.file.close()
        print('Archiver on file {} closed'.format(self.filename))
