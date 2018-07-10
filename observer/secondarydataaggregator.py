from observer.observer import Observer
from observer.archiver import Archiver

class SecondaryDataAggregator(Observer):
    '''
    This class ...
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


    def update(self, data):
        if len(data) == 4:
            # data comming from archive file (mode simulation)
            recordIndex, timestampMilliSec, priceFloat, volumeFloat = data
        else:
            # data comming from exchange (mode real time)
            timestampMilliSec, priceFloat, volumeFloat = data

        self.archiver.update(data)

        if self.isVerbose:
            print('SecondaryDataAggregator: ', end='')
            print(data)


    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        self.archiver.close()
        print('SecondaryDataAggregator closed')
