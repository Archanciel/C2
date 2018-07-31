from observable.observable import Observable
import csv

class ArchivedDatasource(Observable):
    '''
    This class reads in data from a csv trade data archive file and
    notify its Oservers one data line at a time, simulating real time
    data reception from an exchange.

    :seqdiag_note In simulation mode, reads data line by line from a primary data file. For every data line read, calls the notifyObservers(data) method of its parent class, Observable.
    '''

    def __init__(self, filename):
        '''
        Constructor.
        :param filename: name of the file to read data from
        '''
        super().__init__()
        self.file = open(filename, 'r')
        self.reader = csv.reader(self.file, delimiter='\t')
        next(self.reader) #read the header line


    def processArchivedData(self):
        for row in self.reader:
            recordIndex = row[0]
            timestampMilliSec = row[1]
            volumeFloat = row[2]
            priceFloat = row[3]

            self.notifyObservers((recordIndex, timestampMilliSec, volumeFloat, priceFloat))

        self.file.close()
        super().stopObservable()


    def stopObservable(self):
        super().stopObservable()
        self.file.close()