from observable import Observable
from binance.websockets import BinanceSocketManager
from binance.client import Client
import pickle

from apikey.apikeyfilegenerator import ApiKeyFileGenerator


class BinanceDatasource(Observable):
    DECODE_PW = 'c2_pw%&_23'

    def startDataReception(self):

        # obtain from file the binance encoded API keys. This file was created using
        # ApiKeyFileGenerator.
        with open(ApiKeyFileGenerator.FILE_PATH + 'bi.bin', 'rb') as handle:
            encryptedKeyList = pickle.load(handle)

        ap = ApiKeyFileGenerator()

        # decode the keys with the pw used to encode them
        api_key = ap.decode(self.DECODE_PW, encryptedKeyList[0])
        api_secret_key = ap.decode(self.DECODE_PW, encryptedKeyList[1])

        client = Client(api_key, api_secret_key)

        bm = BinanceSocketManager(client)
        # start any sockets here, i.e a trade socket
        conn_key = bm.start_aggtrade_socket('BTCUSDT', self.notifyObservers)
        # then start the socket manager
        bm.start()


    def processData(self, data):
        return data


if __name__ == '__main__':
    bds = BinanceDatasource()
    from observer.archiver import Archiver
    bds.addObserver(Archiver())
    bds.startDataReception()