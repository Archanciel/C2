import pickle
import argparse
import base64
import sys
import os


class ApiKeyFileGenerator:
    def __init__(self):
        if os.name == 'posix':
            self.FILE_PATH = "/sdcard/"  # if executed on Android
        else:
            self.FILE_PATH = "D:/development/python/"  # if executed on Windows

    def getCommandLineArgs(self, argList):
        '''
        Uses argparse to acquire the user command line arguments.

        :param argList: were acquired from sys.argv or set by test code
        :return: apiKey, apiSecretKey, binary file name (without extention), password
        '''
        parser = argparse.ArgumentParser(
            description="Creates a binary file containing the API key and API secret key "
                        "passed as argument. The two keys are encrypted using the passed "
                        "password before being written to the destination file")
        parser.add_argument("-a", "--api_key", required = True, help="API key used to access the remote service.")
        parser.add_argument("-s", "--api_secret_key", required = True, help="API secret key used to access the remote service.")
        parser.add_argument("-f", "--binary_file_name", required = True,
                            help="Binary file name (without extention and without path) "
                                 "which will contain the API key and the API secret key "
                                 "provided as arguments.")
        parser.add_argument("-pw", "--password", required = True,
                            help="Password used to encrypt the the API key and the API "
                                 "secret key in the binary file.")
        args = parser.parse_args(argList)

        return args.api_key, args.api_secret_key, args.binary_file_name, args.password


    def encode(self, key, clear):
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()


    def decode(self, key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)


    def createKeyFile(self, commandLineArgs = None):
        '''
        Usage: python apikeyfilegenerator + arguments
        :param commandLineArgs: only there for unit testing purpose.
        :return:
        '''
        if commandLineArgs == None:
            commandLineArgs = sys.argv[1:]

        # get the user arguments
        apiKey, apiSecretKey, fileName, password = self.getCommandLineArgs(commandLineArgs)

        filePathName = self.FILE_PATH + fileName + '.bin'

        # encoding the api keys
        apiKey = self.encode(password, apiKey)
        apiSecretKey = self.encode(password, apiSecretKey)

        with open(filePathName, 'wb') as handle:
            pickle.dump([apiKey, apiSecretKey], handle)

        encryptedKeyList = None

        with open(filePathName, 'rb') as handle:
            encryptedKeyList = pickle.load(handle)

        keyLabelList = ['api key', 'api secret key']

        print('\nencrypted keys')

        for label, encrypted in zip(keyLabelList, encryptedKeyList):
            print(label + ': ' + encrypted)

        print('\ndecrypted keys')

        for label, encrypted in zip(keyLabelList, encryptedKeyList):
            print(label + ': ' + label, self.decode(password, encrypted))

        print('\nkeys encoded with password : {}. WARNING: password will be required to decode the keys obtained from the binary file !'.format(password))
        print('\nencoded keys stored in ' + filePathName)


if __name__ == '__main__':
    ap = ApiKeyFileGenerator()

    ap.createKeyFile()
