from observer.observer import Observer
import csv

class Archiver(Observer):
    CSV_ROW_HEADER = ["MS TIMESTAMP", "PRICE", "VOLUME"]

    '''
    This class stores the received data into a csv file.
    '''
    def __init__(self, filename):
        '''
        Constructs an instance of Archiver which will write into the passed
        file name. In case the file already exists, it will be overwritten.

        :param filename: name of the file to write in.
        '''

        #creating the output csv file and initializing it with the column titles
        self.filename = filename
        self.file = open(self.filename, 'w', newline = '')
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.CSV_ROW_HEADER)

    def update(self, data):
        timestampMilliSec, priceFloat, volumeFloat = data

        self.writer.writerow([timestampMilliSec, priceFloat, volumeFloat])

        print(data)


    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.file.close()
        print('Archiver on file {} closed'.format(self.filename))
