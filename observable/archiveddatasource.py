from observable.observable import Observable
import csv

class ArchivedDatasource(Observable):
    '''
    This class reads in data from a csv trade data archive file and
    notify its Oservers one data line at a time, simulating real time
    data reception from an exchange.
    '''

    def __init__(self, filename):
        '''
        Constructor.

        :param filename: name of the file to read data from
        '''
        super().__init__()
        self.file = open(filename, 'r')
        self.reader = csv.reader(self.file)
        next(self.reader) #read the header line


    def processArchivedData(self):
        for row in self.reader:
            timestampMilliSec = row[0]
            priceFloat = row[1]
            volumeFloat = row[2]

            self.notifyObservers((timestampMilliSec, priceFloat, volumeFloat))

        self.file.close()
        super().stopObservable()


    def stopObservable(self):
        super().stopObservable()
        self.file.close()