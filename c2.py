import sys
from observable.binancedatasource import BinanceDatasource
from observer.archiver import Archiver


class Controller:
    def __init__(self, tradingPair):
        '''
        Initiate a Controller for the passed trading pair.

        :param tradingPair: example: 'BTCUSDT'
        '''
        self.datasource = BinanceDatasource(tradingPair)
        self.datasource.addObserver(Archiver())


    def start(self):
        '''
        Start the data stream.

        :return:
        '''
        self.datasource.startDataReception()


    def stop(self):
        '''
        Stop the data stream.
        :return:
        '''
        self.datasource.stopDataReception()


if __name__ == '__main__':
    tradePair = 'BTCUSDT'
    c2 = Controller(tradePair)
    print('Starting the Binance aggregate trade stream for pair {}. Type s to stop the stream ...'.format(tradePair))
    c2.start()

    while True:
        if input() == 's':
            print('Stopping the stream ...')
            c2.stop()
            sys.exit(0) #required for the program to exit !