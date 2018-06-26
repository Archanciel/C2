from observable.observable import Observable
from binance.websockets import BinanceSocketManager
from binance.client import Client
import pickle
from twisted.internet import reactor

from apikey.apikeyfilegenerator import ApiKeyFileGenerator


class BinanceDatasource(Observable):
    '''
    This class open a data stream on Binance for receiving in real time
    the aggregates trades on the trading pair specified at construction
    time.

    Definition: The Aggregate Trade Streams push trade information that is
    aggregated for a single taker order.
    '''
    DECODE_PW = 'c2_pw%&_23'

    def __init__(self, tradingPair):
        '''
        Constructor.

        :param tradingPair: example: 'BTCUSDT'
        '''
        super().__init__()
        self.tradingPair = tradingPair
        self.socketManager = None
        self.connectionKey = None

    def startDataReception(self):
        '''
        Start the Binance data stream.

        :return:
        '''

        # obtain from file the binance encoded API keys. This file was created using
        # ApiKeyFileGenerator.
        with open(ApiKeyFileGenerator.FILE_PATH + 'bi.bin', 'rb') as handle:
            encryptedKeyList = pickle.load(handle)

        apiKeyMgr = ApiKeyFileGenerator()

        # decode the keys with the pw used to encode them
        api_key = apiKeyMgr.decode(self.DECODE_PW, encryptedKeyList[0])
        api_secret_key = apiKeyMgr.decode(self.DECODE_PW, encryptedKeyList[1])

        binanceClient = Client(api_key, api_secret_key)

        self.socketManager = BinanceSocketManager(binanceClient)
        # start any sockets here, i.e a trade socket
        self.connectionKey = self.socketManager.start_aggtrade_socket(self.tradingPair, self.notifyObservers)
        # then start the socket manager
        self.socketManager.start()


    def stopDataReception(self):
        '''
        Stop the Binance data stream.

        :return:
        '''
        self.socketManager.stop_socket(self.connectionKey)

        # required for the program to exit
        reactor.stop()


    def processData(self, data):
        '''
        Process the raw data received from Binance before sending it to
        the Observer.

        :param data: raw data streamed by Binance in the form of a
        dictionary structured as
            {
              "e": "aggTrade",  // Event type
              "E": 123456789,   // Event time
              "s": "BNBBTC",    // Symbol
              "a": 12345,       // Aggregate trade ID
              "p": "0.001",     // Price
              "q": "100",       // Quantity
              "f": 100,         // First trade ID
              "l": 105,         // Last trade ID
              "T": 123456785,   // Trade time
              "m": true,        // Is the buyer the market maker?
              "M": true         // Ignore.
            }
        :return:
        '''
        timestamp = data['T']
        price = data['p']
        volume = data['q']

        return timestamp, price, volume


if __name__ == '__main__':
    bds = BinanceDatasource('BTCUSDT')
    from observer.archiver import Archiver
    bds.addObserver(Archiver())
    bds.startDataReception()