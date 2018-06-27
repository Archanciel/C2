from observer.observer import Observer
from observer.archiver import Archiver

class Notifyer(Observer):
    '''
    This class ...
    '''
    def __init__(self, secondaryDataFilename):
        '''
        Constructs an instance of Notifyer which computes the secndary data.

        :param filename: name of the file to write in.
        '''

        #creating the output csv file and initializing it with the column titles
        self.archiver = Archiver(secondaryDataFilename)


    def update(self, data):
        timestampMilliSec, priceFloat, volumeFloat = data

        self.archiver.update(data)

        print('Notifyer: ',end = '')
        print(data)


    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.archiver.close()
        print('Notifyer closed')
