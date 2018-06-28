import sys
from observable.binancedatasource import BinanceDatasource
from observer.archiver import Archiver


class Controller:
    '''
    This class is the entry point of the C2 application.
    '''
    def __init__(self):
        '''
        Initiate a Controller for the passed trading pair.

        :param tradingPair: example: 'BTCUSDT'
        '''
        self.datasource = None
        self.primaryDataFile = None

    def start(self, tradingPair):
        '''
        Start the data stream.

        :return:
        '''
        self.datasource = BinanceDatasource(tradingPair)
        self.primaryDataFile = 'primary.csv'
        self.datasource.addObserver(Archiver(self.primaryDataFile))
        self.datasource.startDataReception()


    def stop(self):
        '''
        Stop the data stream.
        :return:
        '''
        self.datasource.stopObservable()


if __name__ == '__main__':
    tradePair = 'BTCUSDT'
    c2 = Controller()
    print('Starting the Binance aggregate trade stream for pair {}. Type s to stop the stream ...'.format(tradePair))
    c2.start(tradePair)

    while True:
        if input() == 's':
            print('Stopping the stream ...')
            c2.stop()
            sys.exit(0) #required for the program to exit !